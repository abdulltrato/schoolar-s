from core.viewsets import RobustModelViewSet
from .models import UserProfile
from .serializers import UserProfileSerializer


class UserProfileViewSet(RobustModelViewSet):
    queryset = UserProfile.objects.select_related("school", "user")
    serializer_class = UserProfileSerializer
    search_fields = ("user__username", "role", "tenant_id")
