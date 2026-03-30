from core.viewsets import RobustModelViewSet
# ViewSet base com tratamento robusto.
from .models import UserProfile
# Modelo de perfil escolar.
from .serializers import UserProfileSerializer
# Serializer correspondente.


class UserProfileViewSet(RobustModelViewSet):
    """CRUD de perfis de usuário, com joins para escola e user."""
    queryset = UserProfile.objects.select_related("school", "user")
    serializer_class = UserProfileSerializer
    search_fields = ("user__username", "role", "tenant_id")
