import logging

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.utils import timezone
from django.db.models import Q
from rest_framework import filters, viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.exceptions import PermissionDenied

from core.models import tenant_id_from_user

from .permissions import RoleBasedAccessPermission

audit_logger = logging.getLogger("schoolar.audit")


class ValidatedSearchOrderingMixin:
    @classmethod
    def _infer_model(cls):
        queryset = getattr(cls, "queryset", None)
        if queryset is not None and getattr(queryset, "model", None) is not None:
            return queryset.model
        serializer_class = getattr(cls, "serializer_class", None)
        return getattr(getattr(serializer_class, "Meta", None), "model", None)

    @classmethod
    def _field_exists(cls, model, field_path):
        current_model = model
        for index, part in enumerate(field_path.split("__")):
            if part == "pk" and index == len(field_path.split("__")) - 1:
                return True
            try:
                field = current_model._meta.get_field(part)
            except FieldDoesNotExist:
                return False
            if index < len(field_path.split("__")) - 1:
                if not getattr(field, "is_relation", False) or not getattr(field, "related_model", None):
                    return False
                current_model = field.related_model
        return True

    @classmethod
    def _sanitize_fields(cls, fields):
        model = cls._infer_model()
        if model is None or not fields:
            return fields
        valid_fields = []
        for field in fields:
            normalized = field.lstrip("^=@$-")
            if normalized == "__all__" or cls._field_exists(model, normalized):
                valid_fields.append(field)
        return tuple(valid_fields)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "search_fields"):
            cls.search_fields = cls._sanitize_fields(getattr(cls, "search_fields", ()))
        if hasattr(cls, "ordering_fields"):
            cls.ordering_fields = cls._sanitize_fields(getattr(cls, "ordering_fields", ()))


class TenantScopedQuerysetMixin:
    tenant_field_name = "tenant_id"
    ADMIN_ROLES = {"national_admin", "provincial_admin", "district_admin"}

    def _get_profile(self):
        user = getattr(self.request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return None
        profile = getattr(user, "school_profile", None)
        if profile is not None and getattr(profile, "deleted_at", None) is not None:
            return None
        return profile

    def _resolve_tenant_id(self):
        profile = self._get_profile()
        header_tenant = getattr(self.request, "tenant_id", None)
        header_tenant = (header_tenant or "").strip() or None

        user = getattr(self.request, "user", None)
        user_tenant = tenant_id_from_user(user) if user and getattr(user, "is_authenticated", False) else ""
        user_tenant = (user_tenant or "").strip() or None
        if user_tenant:
            if header_tenant and header_tenant != user_tenant:
                raise PermissionDenied("O header X-Tenant-ID deve coincidir com o tenant do usuário autenticado.")
            return user_tenant

        if not profile:
            return header_tenant

        if header_tenant:
            return header_tenant

        if profile.role in self.ADMIN_ROLES:
            return None
        return None

    def _get_model(self):
        queryset = super().get_queryset()
        return getattr(queryset, "model", None)

    def _has_tenant_field(self, model):
        if model is None:
            return False
        try:
            model._meta.get_field(self.tenant_field_name)
            return True
        except FieldDoesNotExist:
            return False

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant_id = self._resolve_tenant_id()
        model = getattr(queryset, "model", None)
        if tenant_id and self._has_tenant_field(model):
            return queryset.filter(**{self.tenant_field_name: tenant_id})
        if self._has_tenant_field(model):
            profile = self._get_profile()
            if profile and profile.role not in self.ADMIN_ROLES and not (profile.tenant_id or "").strip():
                raise PermissionDenied("Tenant header is required for this resource.")
        return queryset

    def perform_create(self, serializer):
        tenant_id = self._resolve_tenant_id()
        model = getattr(getattr(serializer, "Meta", None), "model", None)
        if tenant_id and self._has_tenant_field(model):
            serializer.save(**{self.tenant_field_name: tenant_id})
            return
        if self._has_tenant_field(model):
            profile = self._get_profile()
            if profile and profile.role not in self.ADMIN_ROLES and not (profile.tenant_id or "").strip():
                raise PermissionDenied("Tenant header is required for this resource.")
        super().perform_create(serializer)

    def perform_update(self, serializer):
        tenant_id = self._resolve_tenant_id()
        model = getattr(getattr(serializer, "Meta", None), "model", None)
        if tenant_id and self._has_tenant_field(model):
            instance = serializer.instance
            current_tenant_id = getattr(instance, self.tenant_field_name, None)
            if current_tenant_id and current_tenant_id != tenant_id:
                raise PermissionDenied("Record belongs to a different tenant.")
            serializer.save(**{self.tenant_field_name: tenant_id})
            return
        if self._has_tenant_field(model):
            profile = self._get_profile()
            if profile and profile.role not in self.ADMIN_ROLES and not (profile.tenant_id or "").strip():
                raise PermissionDenied("Tenant header is required for this resource.")
        super().perform_update(serializer)


class RoleScopedQuerysetMixin:
    def _get_profile(self):
        user = getattr(self.request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return None
        return getattr(user, "school_profile", None)

    def _scope_queryset_for_role(self, queryset):
        profile = self._get_profile()
        if profile is None or not profile.active:
            return queryset

        role = profile.role
        user = self.request.user
        model = getattr(queryset, "model", None)
        model_name = getattr(getattr(model, "_meta", None), "model_name", "")
        tenant_id = (profile.tenant_id or "").strip()

        if role in {"national_admin", "provincial_admin", "district_admin"}:
            return queryset

        if role in {"school_director", "finance_officer", "support"}:
            if tenant_id and TenantScopedQuerysetMixin._has_tenant_field(self, model):
                return queryset.filter(tenant_id=tenant_id)
            return queryset

        if role == "teacher":
            if tenant_id and TenantScopedQuerysetMixin._has_tenant_field(self, model):
                queryset = queryset.filter(tenant_id=tenant_id)
            teacher_filters = {
                "teacher": Q(user=user),
                "classroom": Q(lead_teacher__user=user),
                "teachingassignment": Q(teacher__user=user),
                "assessment": Q(teaching_assignment__teacher__user=user),
                "subjectperiodresult": Q(teaching_assignment__teacher__user=user),
                "attendancerecord": Q(enrollment__classroom__lead_teacher__user=user),
                "announcement": Q(author=user) | Q(audience="teachers"),
                "courseoffering": Q(teacher__user=user),
                "lesson": Q(offering__teacher__user=user),
                "lessonmaterial": Q(lesson__offering__teacher__user=user),
                "assignment": Q(offering__teacher__user=user),
                "submission": Q(assignment__offering__teacher__user=user),
            }
            role_filter = teacher_filters.get(model_name)
            return queryset.filter(role_filter) if role_filter is not None else queryset

        if role == "student":
            student_filters = {
                "student": Q(user=user),
                "enrollment": Q(student__user=user),
                "assessment": Q(student__user=user),
                "subjectperiodresult": Q(student__user=user),
                "invoice": Q(student__user=user),
                "payment": Q(invoice__student__user=user),
                "attendancerecord": Q(enrollment__student__user=user),
                "classroom": Q(enrollment__student__user=user),
                "announcement": Q(audience__in=["students", "school", "classroom"]),
                "submission": Q(student__user=user),
                "course": Q(offerings__classroom__enrollment__student__user=user),
                "courseoffering": Q(classroom__enrollment__student__user=user),
                "lesson": Q(offering__classroom__enrollment__student__user=user),
                "lessonmaterial": Q(lesson__offering__classroom__enrollment__student__user=user),
                "assignment": Q(offering__classroom__enrollment__student__user=user),
            }
            role_filter = student_filters.get(model_name)
            scoped = queryset.filter(role_filter) if role_filter is not None else queryset.none()
            return scoped.distinct()

        if role == "guardian":
            guardian_filters = {
                "guardian": Q(user=user),
                "studentguardian": Q(guardian__user=user),
                "student": Q(studentguardian__guardian__user=user),
                "enrollment": Q(student__studentguardian__guardian__user=user),
                "assessment": Q(student__studentguardian__guardian__user=user),
                "subjectperiodresult": Q(student__studentguardian__guardian__user=user),
                "invoice": Q(student__studentguardian__guardian__user=user),
                "payment": Q(invoice__student__studentguardian__guardian__user=user),
                "attendancerecord": Q(enrollment__student__studentguardian__guardian__user=user),
                "classroom": Q(enrollment__student__studentguardian__guardian__user=user),
                "announcement": Q(audience__in=["guardians", "school", "classroom"]),
                "submission": Q(student__studentguardian__guardian__user=user),
                "course": Q(offerings__classroom__enrollment__student__studentguardian__guardian__user=user),
                "courseoffering": Q(classroom__enrollment__student__studentguardian__guardian__user=user),
                "lesson": Q(offering__classroom__enrollment__student__studentguardian__guardian__user=user),
                "lessonmaterial": Q(lesson__offering__classroom__enrollment__student__studentguardian__guardian__user=user),
                "assignment": Q(offering__classroom__enrollment__student__studentguardian__guardian__user=user),
            }
            role_filter = guardian_filters.get(model_name)
            scoped = queryset.filter(role_filter) if role_filter is not None else queryset.none()
            return scoped.distinct()

        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        return self._scope_queryset_for_role(queryset)


class RobustModelViewSet(ValidatedSearchOrderingMixin, RoleScopedQuerysetMixin, TenantScopedQuerysetMixin, viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ("id",)
    ordering = ("id",)
    permission_classes = [RoleBasedAccessPermission]
    audit_resource = None

    def _configured_request_user_field_names(self, model) -> tuple[str, ...]:
        configured: list[str] = []
        for attr in ("REQUEST_USER_CREATE_FIELD", "REQUEST_USER_UPDATE_FIELD"):
            name = getattr(model, attr, None)
            if name:
                configured.append(name)
        for attr in ("REQUEST_USER_CREATE_FIELDS", "REQUEST_USER_UPDATE_FIELDS"):
            names = getattr(model, attr, None) or ()
            configured.extend(list(names))

        seen = set()
        normalized = []
        for name in configured:
            name = (name or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            normalized.append(name)
        return tuple(normalized)

    def _assert_request_user_fields_readonly(self, serializer) -> None:
        initial_data = getattr(serializer, "initial_data", None)
        if not isinstance(initial_data, dict):
            return

        model = getattr(getattr(serializer, "Meta", None), "model", None)
        if model is None:
            return

        forbidden = set(self._configured_request_user_field_names(model))
        if not forbidden:
            return

        errors = {}
        for field_name in forbidden:
            if field_name in initial_data:
                errors[field_name] = "Este campo é definido automaticamente e é somente leitura."

        if errors:
            raise DRFValidationError(errors)

    def _build_audit_payload(self, *, action, instance, changed_fields=None):
        request = getattr(self, "request", None)
        user = getattr(request, "user", None)
        profile = getattr(user, "school_profile", None) if user and getattr(user, "is_authenticated", False) else None
        return {
            "event": "resource_mutation",
            "action": action,
            "resource": self.audit_resource or getattr(instance._meta, "model_name", "resource"),
            "object_id": getattr(instance, "pk", None),
            "changed_fields": changed_fields or [],
            "request_id": getattr(request, "request_id", None),
            "tenant_id": getattr(instance, "tenant_id", "") or getattr(profile, "tenant_id", "") if profile else "",
            "role": getattr(profile, "role", None) if profile else None,
            "user_id": getattr(user, "id", None) if user and getattr(user, "is_authenticated", False) else None,
            "username": getattr(user, "username", None) if user and getattr(user, "is_authenticated", False) else None,
            "path": request.get_full_path() if request else None,
            "method": request.method if request else None,
        }

    def _audit_mutation(self, *, action, instance, changed_fields=None):
        if not self.audit_resource:
            return
        payload = self._build_audit_payload(
            action=action,
            instance=instance,
            changed_fields=changed_fields,
        )
        audit_logger.info("resource_mutation", extra=payload)

        AuditEvent = apps.get_model("school", "AuditEvent")
        AuditEvent.objects.create(
            resource=payload["resource"],
            action=payload["action"],
            object_id=payload["object_id"] or 0,
            object_repr=str(instance)[:255],
            tenant_id=payload["tenant_id"] or "",
            request_id=payload["request_id"] or "",
            path=payload["path"] or "",
            method=payload["method"] or "",
            role=payload["role"] or "",
            username=payload["username"] or "",
            changed_fields=payload["changed_fields"] or [],
        )
        self._generate_audit_alerts(payload)

    def _generate_audit_alerts(self, payload):
        AuditEvent = apps.get_model("school", "AuditEvent")
        AuditAlert = apps.get_model("school", "AuditAlert")

        window_start = timezone.now() - timezone.timedelta(hours=24)
        base_queryset = AuditEvent.objects.filter(created_at__gte=window_start)
        tenant_id = payload.get("tenant_id") or ""
        if tenant_id:
            base_queryset = base_queryset.filter(tenant_id=tenant_id)

        recent_count = base_queryset.count()
        actor_count = base_queryset.filter(username=payload.get("username") or "").count() if payload.get("username") else 0
        resource_count = base_queryset.filter(resource=payload.get("resource") or "").count() if payload.get("resource") else 0

        alerts_to_create = []
        if recent_count >= 10:
            alerts_to_create.append({
                "alert_type": "high_recent_volume",
                "severity": "elevated" if recent_count >= 20 else "watch",
                "summary": f"{recent_count} audit events in the last 24h.",
                "resource": payload.get("resource") or "",
                "username": payload.get("username") or "",
                "tenant_id": tenant_id,
                "details": {"recent_count": recent_count},
            })
        if actor_count >= 5 and payload.get("username"):
            alerts_to_create.append({
                "alert_type": "actor_concentration",
                "severity": "elevated" if actor_count >= 10 else "watch",
                "summary": f"{payload['username']} generated {actor_count} audit events in the last 24h.",
                "resource": payload.get("resource") or "",
                "username": payload["username"],
                "tenant_id": tenant_id,
                "details": {"actor_count": actor_count},
            })
        if resource_count >= 6 and payload.get("resource"):
            alerts_to_create.append({
                "alert_type": "resource_concentration",
                "severity": "elevated" if resource_count >= 12 else "watch",
                "summary": f"{payload['resource']} generated {resource_count} audit events in the last 24h.",
                "resource": payload["resource"],
                "username": payload.get("username") or "",
                "tenant_id": tenant_id,
                "details": {"resource_count": resource_count},
            })

        for alert in alerts_to_create:
            exists = AuditAlert.objects.filter(
                alert_type=alert["alert_type"],
                severity=alert["severity"],
                tenant_id=alert["tenant_id"],
                resource=alert["resource"],
                username=alert["username"],
                created_at__gte=window_start,
                acknowledged=False,
            ).exists()
            if not exists:
                AuditAlert.objects.create(**alert)

    def perform_create(self, serializer):
        self._assert_request_user_fields_readonly(serializer)
        super().perform_create(serializer)
        self._audit_mutation(action="create", instance=serializer.instance)

    def perform_update(self, serializer):
        self._assert_request_user_fields_readonly(serializer)
        changed_fields = sorted(serializer.validated_data.keys())
        super().perform_update(serializer)
        self._audit_mutation(action="update", instance=serializer.instance, changed_fields=changed_fields)
