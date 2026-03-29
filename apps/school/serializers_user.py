from rest_framework import serializers

from .models import UserProfile, Teacher


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"


class TeacherSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"
