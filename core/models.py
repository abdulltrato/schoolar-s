import secrets

from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection, models
from django.utils import timezone


class TenantModel(models.Model):
    tenant_id = models.CharField(max_length=50, blank=True, verbose_name="Identificador do tenant")

    REQUEST_USER_CREATE_FIELD = None
    REQUEST_USER_CREATE_FIELDS: tuple[str, ...] = ()
    REQUEST_USER_UPDATE_FIELD = None
    REQUEST_USER_UPDATE_FIELDS: tuple[str, ...] = ()

    class Meta:
        abstract = True

    def normalize_tenant_id(self):
        self.tenant_id = (self.tenant_id or "").strip()
        return self.tenant_id

    def _resolve_request_user(self):
        try:
            from core.request_context import get_current_request
        except Exception:
            return None

        request = get_current_request()
        if not request:
            return None

        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            return user
        return None

    def _configured_request_user_field_names(self):
        configured = []
        single_create = getattr(self.__class__, "REQUEST_USER_CREATE_FIELD", None)
        if single_create:
            configured.append(single_create)
        single_update = getattr(self.__class__, "REQUEST_USER_UPDATE_FIELD", None)
        if single_update:
            configured.append(single_update)

        plural_create = getattr(self.__class__, "REQUEST_USER_CREATE_FIELDS", None) or ()
        configured.extend(list(plural_create))
        plural_update = getattr(self.__class__, "REQUEST_USER_UPDATE_FIELDS", None) or ()
        configured.extend(list(plural_update))

        seen = set()
        normalized = []
        for name in configured:
            name = (name or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            normalized.append(name)
        return tuple(normalized)

    def _sync_request_user_fields(self) -> None:
        request_user = self._resolve_request_user()
        if not request_user:
            return

        def set_user(field_name: str) -> None:
            try:
                field = self._meta.get_field(field_name)
            except FieldDoesNotExist as exc:
                raise ValidationError({field_name: "Invalid REQUEST_USER_* configuration."}) from exc

            if not getattr(field, "is_relation", False) or not (
                getattr(field, "many_to_one", False) or getattr(field, "one_to_one", False)
            ):
                raise ValidationError({field_name: "REQUEST_USER_* fields must be a FK/O2O to the user model."})

            try:
                user_model = get_user_model()
            except Exception:
                user_model = None

            remote_model = getattr(getattr(field, "remote_field", None), "model", None)
            if user_model is not None:
                if isinstance(remote_model, str):
                    if remote_model != getattr(settings, "AUTH_USER_MODEL", ""):
                        raise ValidationError({field_name: "REQUEST_USER_* fields must point to AUTH_USER_MODEL."})
                else:
                    if not (hasattr(remote_model, "_meta") and remote_model._meta.label == user_model._meta.label):
                        raise ValidationError({field_name: "REQUEST_USER_* fields must point to AUTH_USER_MODEL."})

            setattr(self, field_name, request_user)

        create_field = getattr(self.__class__, "REQUEST_USER_CREATE_FIELD", None)
        create_fields = getattr(self.__class__, "REQUEST_USER_CREATE_FIELDS", None) or ()
        create_names = [*( [create_field] if create_field else [] ), *list(create_fields)]

        update_field = getattr(self.__class__, "REQUEST_USER_UPDATE_FIELD", None)
        update_fields = getattr(self.__class__, "REQUEST_USER_UPDATE_FIELDS", None) or ()
        update_names = [*( [update_field] if update_field else [] ), *list(update_fields)]

        normalized_create_names = []
        for field_name in create_names:
            field_name = (field_name or "").strip()
            if field_name:
                normalized_create_names.append(field_name)

        normalized_update_names = []
        for field_name in update_names:
            field_name = (field_name or "").strip()
            if field_name:
                normalized_update_names.append(field_name)

        if not self.pk:
            for field_name in normalized_create_names:
                set_user(field_name)
        else:
            manager = getattr(self.__class__, "all_objects", None) or self.__class__._default_manager
            for field_name in normalized_create_names:
                stored_id = manager.filter(pk=self.pk).values_list(f"{field_name}_id", flat=True).first()
                current_id = getattr(self, f"{field_name}_id", None)
                if stored_id is None:
                    set_user(field_name)
                    continue
                if current_id != stored_id:
                    raise ValidationError({field_name: "Este campo é definido automaticamente e não pode ser alterado."})

        for field_name in normalized_update_names:
            set_user(field_name)

    def require_tenant_id(self):
        if not self.normalize_tenant_id():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        return self.tenant_id

    def inherit_tenant_from_user(self, user, *, overwrite: bool = False) -> str:
        tenant_id = tenant_id_from_user(user)
        if tenant_id and (overwrite or not (self.tenant_id or "").strip()):
            self.tenant_id = tenant_id
        return tenant_id

    def _infer_user_relation_fields(self):
        try:
            user_model = get_user_model()
        except Exception:
            user_model = None

        excluded_field_names = set(self._configured_request_user_field_names() or ())

        inferred = []
        for field in self._meta.get_fields():
            if getattr(field, "auto_created", False):
                continue
            if field.name in excluded_field_names:
                continue
            if not getattr(field, "is_relation", False):
                continue
            if not (getattr(field, "many_to_one", False) or getattr(field, "one_to_one", False)):
                continue

            remote_model = getattr(getattr(field, "remote_field", None), "model", None)
            if remote_model is None:
                continue

            if user_model is not None and remote_model is user_model:
                inferred.append(field.name)
                continue
            if isinstance(remote_model, str) and remote_model == getattr(settings, "AUTH_USER_MODEL", ""):
                inferred.append(field.name)
                continue
            if user_model is not None and hasattr(remote_model, "_meta") and remote_model._meta.label == user_model._meta.label:
                inferred.append(field.name)
                continue

        return tuple(inferred)

    def _inherit_tenant_from_related_users(self) -> str:
        field_names = getattr(self, "TENANT_INHERIT_USER_FIELDS", None)
        if field_names is None:
            field_name = getattr(self, "TENANT_INHERIT_USER_FIELD", None)
            if field_name:
                field_names = (field_name,)
            else:
                field_names = self._infer_user_relation_fields()

        for field_name in field_names or ():
            try:
                related_user = getattr(self, field_name, None)
            except Exception:
                related_user = None
            if not related_user:
                continue

            related_tenant = tenant_id_from_user(related_user)
            if not related_tenant:
                continue

            current = (self.tenant_id or "").strip()
            if current and current != related_tenant:
                raise ValidationError({"tenant_id": "tenant_id must match the related user's tenant."})
            if not current:
                self.tenant_id = related_tenant
            return related_tenant

        return ""

    def _resolve_request_tenant_id(self) -> str:
        try:
            from core.request_context import get_current_request
        except Exception:
            return ""

        request = get_current_request()
        if not request:
            return ""

        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            user_tenant_id = tenant_id_from_user(user)
        else:
            user_tenant_id = ""

        header_tenant_id = getattr(request, "tenant_id", None)
        if not header_tenant_id:
            headers = getattr(request, "headers", None)
            if headers:
                header_tenant_id = headers.get("X-Tenant-ID")
            if not header_tenant_id:
                header_tenant_id = request.META.get("HTTP_X_TENANT_ID")
        header_tenant_id = (header_tenant_id or "").strip()

        if user_tenant_id:
            if header_tenant_id and header_tenant_id != user_tenant_id:
                raise ValidationError({"tenant_id": "tenant_id must match the current user's tenant."})
            return user_tenant_id
        return header_tenant_id

    def _sync_tenant_with_request(self) -> str:
        tenant_id = self._resolve_request_tenant_id()
        if tenant_id:
            current = (self.tenant_id or "").strip()
            if current and current != tenant_id:
                raise ValidationError({"tenant_id": "tenant_id must match the current user's tenant."})
            self.tenant_id = tenant_id
            return tenant_id

        if not (self.tenant_id or "").strip():
            return self._inherit_tenant_from_related_users()
        self._inherit_tenant_from_related_users()
        return (self.tenant_id or "").strip()

    def full_clean(self, *args, **kwargs):
        self._sync_request_user_fields()
        self._sync_tenant_with_request()
        return super().full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self._sync_request_user_fields()
        self._sync_tenant_with_request()
        return super().save(*args, **kwargs)


def tenant_id_from_user(user) -> str:
    if not user:
        return ""
    direct = (getattr(user, "tenant_id", "") or "").strip()
    if direct:
        return direct
    profile = getattr(user, "school_profile", None)
    if profile is not None and getattr(profile, "deleted_at", None) is not None:
        return ""
    return (getattr(profile, "tenant_id", "") or "").strip()


class AuditModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Criado em")
    updated_at = models.DateTimeField(default=timezone.now, verbose_name="Atualizado em")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.created_at:
            self.created_at = now
        self.updated_at = now

        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            fields = set(update_fields)
            fields.add("updated_at")
            if not self.pk:
                fields.add("created_at")
            kwargs["update_fields"] = list(fields)

        return super().save(*args, **kwargs)


class TenantAuditModel(TenantModel, AuditModel):
    class Meta:
        abstract = True


class CustomIdentifierMixin(models.Model):
    """
    Generates a predictable identifier composed of a prefix, the current year, a global sequence, and a random suffix.

    The sequence is backed by a PostgreSQL sequence named after the model table (``{table}_custom_id_seq``).
    """

    custom_id = models.CharField(
        db_column="custom_id",
        max_length=48,
        unique=True,
        db_index=True,
        editable=False,
        blank=True,
        null=True,
        verbose_name="Código personalizado",
    )

    CUSTOM_ID_PREFIX = None
    CUSTOM_ID_DATE_FORMAT = "%Y"
    CUSTOM_ID_SEQUENCE_WIDTH = 6
    CUSTOM_ID_RANDOM_WIDTH = 6

    class Meta:
        abstract = True

    # -----------------------------------------------------

    @classmethod
    def _custom_sequence_name(cls):
        return f"{cls._meta.db_table}_custom_id_seq"

    @classmethod
    def _next_sequence(cls):
        sequence_name = cls._custom_sequence_name()
        with connection.cursor() as cursor:
            cursor.execute("SELECT nextval(%s)", [sequence_name])
            return cursor.fetchone()[0]

    @classmethod
    def _custom_id_prefix(cls):
        prefix = getattr(cls, "CUSTOM_ID_PREFIX", None) or getattr(cls, "prefix", None)
        if prefix:
            return str(prefix).upper()
        return cls.__name__[:3].upper()

    # -----------------------------------------------------

    def _random_suffix(self) -> str:
        width = getattr(self, "CUSTOM_ID_RANDOM_WIDTH", 0) or 0
        if width <= 0:
            return ""
        upper = 10 ** width
        return f"{secrets.randbelow(upper):0{width}d}"

    def generate_identifier(self):
        if self.custom_id:
            return

        prefix = self._custom_id_prefix()
        if not prefix:
            return

        date_label = timezone.localtime(timezone.now()).strftime(self.CUSTOM_ID_DATE_FORMAT)
        sequence_number = self.__class__._next_sequence()
        sequence_label = f"{sequence_number:0{self.CUSTOM_ID_SEQUENCE_WIDTH}d}"
        random_label = self._random_suffix()

        self.custom_id = f"{prefix}{date_label}{sequence_label}{random_label}"

    def save(self, *args, **kwargs):
        if not self.custom_id:
            self.generate_identifier()

        return super().save(*args, **kwargs)


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)

    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().alive()


class AllObjectsManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    pass


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Removido em")

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, using=None, keep_parents=False, hard=False):
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)
        if self.deleted_at is None:
            self.deleted_at = timezone.now()
            self.save(update_fields=["deleted_at"])
        return 1, {self._meta.label: 1}

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        if self.deleted_at is None:
            return
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])


class CodeModel(models.Model):
    code = models.CharField(max_length=60, blank=True, verbose_name="Código")

    CODE_PREFIX = None
    CODE_DATE_FORMAT = "%d%m%Y"
    CODE_ORDER_WIDTH = 4
    AUTO_CODE = True

    class Meta:
        abstract = True

    def _code_queryset(self):
        manager = getattr(self.__class__, "all_objects", None)
        return manager if manager is not None else self.__class__.objects

    def _code_prefix(self) -> str:
        prefix = self.CODE_PREFIX
        if prefix:
            return str(prefix).upper()
        return self.__class__.__name__[:3].upper()

    def _generate_code(self) -> str:
        prefix = self._code_prefix()
        date_label = timezone.localtime(timezone.now()).strftime(self.CODE_DATE_FORMAT)
        base = f"{prefix}-{date_label}-"

        queryset = self._code_queryset().filter(code__startswith=base)
        last_code = queryset.order_by("-code").values_list("code", flat=True).first()
        if last_code:
            try:
                last_order = int(str(last_code).rsplit("-", 1)[-1])
                next_order = last_order + 1
            except (ValueError, TypeError):
                next_order = queryset.count() + 1
        else:
            next_order = 1

        return f"{base}{next_order:0{self.CODE_ORDER_WIDTH}d}"

    def save(self, *args, **kwargs):
        if self.AUTO_CODE and not (self.code or "").strip():
            self.code = self._generate_code()
        return super().save(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        if self.AUTO_CODE and not (self.code or "").strip():
            self.code = self._generate_code()
        return super().full_clean(*args, **kwargs)


class NamedModel(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nome")

    class Meta:
        abstract = True


class BaseModel(TenantModel, AuditModel, SoftDeleteModel):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="+",
        verbose_name="Usuário",
    )

    REQUEST_USER_CREATE_FIELD = "usuario"

    class Meta:
        abstract = True


class BaseCodeModel(CodeModel, BaseModel):
    class Meta:
        abstract = True


class BaseNamedCodeModel(NamedModel, BaseCodeModel):
    class Meta:
        abstract = True
