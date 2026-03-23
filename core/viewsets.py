from django.core.exceptions import FieldDoesNotExist
from rest_framework import filters, viewsets
from rest_framework.exceptions import PermissionDenied


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

    def _get_request_tenant_id(self):
        return getattr(self.request, "tenant_id", None)

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
        tenant_id = self._get_request_tenant_id()
        model = getattr(queryset, "model", None)
        if tenant_id and self._has_tenant_field(model):
            return queryset.filter(**{self.tenant_field_name: tenant_id})
        return queryset

    def perform_create(self, serializer):
        tenant_id = self._get_request_tenant_id()
        model = getattr(getattr(serializer, "Meta", None), "model", None)
        if tenant_id and self._has_tenant_field(model):
            serializer.save(**{self.tenant_field_name: tenant_id})
            return
        super().perform_create(serializer)

    def perform_update(self, serializer):
        tenant_id = self._get_request_tenant_id()
        model = getattr(getattr(serializer, "Meta", None), "model", None)
        if tenant_id and self._has_tenant_field(model):
            instance = serializer.instance
            current_tenant_id = getattr(instance, self.tenant_field_name, None)
            if current_tenant_id and current_tenant_id != tenant_id:
                raise PermissionDenied("Record belongs to a different tenant.")
            serializer.save(**{self.tenant_field_name: tenant_id})
            return
        super().perform_update(serializer)


class RobustModelViewSet(ValidatedSearchOrderingMixin, TenantScopedQuerysetMixin, viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ("id",)
    ordering = ("id",)
