from rest_framework.decorators import action
from rest_framework.response import Response

from core.viewsets import RobustModelViewSet

from .models import Transfer
from .serializers import TransferSerializer


class TransferViewSet(RobustModelViewSet):
    queryset = Transfer.objects.select_related(
        "student",
        "teacher",
        "from_school",
        "to_school",
        "from_classroom",
        "to_classroom",
        "new_specialty",
    ).all()
    serializer_class = TransferSerializer
    search_fields = (
        "code",
        "tenant_id",
        "student__name",
        "teacher__name",
        "from_school__name",
        "to_school__name",
        "from_classroom__name",
        "to_classroom__name",
        "status",
    )
    ordering_fields = ("id", "code", "tenant_id", "status", "created_at", "applied_at")
    ordering = ("-created_at",)
    audit_resource = "transfer"

    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director"},
        "update": set(),
        "partial_update": set(),
        "destroy": set(),
    }

    @action(detail=True, methods=["post"], url_path="apply")
    def apply(self, request, pk=None):
        transfer = self.get_object()
        transfer.apply()
        serializer = self.get_serializer(transfer)
        return Response(serializer.data)
