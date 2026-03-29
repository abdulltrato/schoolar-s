from core.viewsets import RobustModelViewSet
from .models import Announcement, ManagementAssignment
from .serializers import AnnouncementSerializer, ManagementAssignmentSerializer


class ManagementAssignmentViewSet(RobustModelViewSet):
    queryset = ManagementAssignment.objects.select_related("teacher", "school", "academic_year")
    serializer_class = ManagementAssignmentSerializer


class AnnouncementViewSet(RobustModelViewSet):
    queryset = Announcement.objects.select_related("school", "classroom", "author")
    serializer_class = AnnouncementSerializer
