from rest_framework import serializers
# Base de serializers do DRF.

from .models import Announcement
# Modelo de comunicado.


class AnnouncementSerializer(serializers.ModelSerializer):
    """Serializa comunicados exibindo nomes de escola, turma e autor."""

    school_name = serializers.CharField(source="school.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Announcement
        fields = "__all__"
