from rest_framework import serializers
# Base de serializers do DRF.

from .models import UserProfile, Teacher
# Modelos de perfil e professor.


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializa perfis de usuário expondo username e nome da escola."""

    username = serializers.CharField(source="user.username", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"


class TeacherSerializer(serializers.ModelSerializer):
    """Serializa professores incluindo nome da escola."""

    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"
