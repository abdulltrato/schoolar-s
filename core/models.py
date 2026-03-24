from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TenantModel(models.Model):
    tenant_id = models.CharField(max_length=50, blank=True, verbose_name="Identificador do tenant")

    class Meta:
        abstract = True

    def normalize_tenant_id(self):
        self.tenant_id = (self.tenant_id or "").strip()
        return self.tenant_id

    def require_tenant_id(self):
        if not self.normalize_tenant_id():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        return self.tenant_id


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


class NamedModel(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nome")

    class Meta:
        abstract = True


class BaseModel(TenantModel, AuditModel, SoftDeleteModel):
    class Meta:
        abstract = True


class BaseCodeModel(CodeModel, BaseModel):
    class Meta:
        abstract = True


class BaseNamedCodeModel(NamedModel, BaseCodeModel):
    class Meta:
        abstract = True
