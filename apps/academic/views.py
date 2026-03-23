from core.viewsets import RobustModelViewSet

from .models import Student
from .serializers import StudentSerializer


class StudentViewSet(RobustModelViewSet):
    queryset = Student.objects.prefetch_related("studentcompetency_set__competency").all()
    serializer_class = StudentSerializer
    search_fields = ("name", "estado")
    ordering_fields = ("id", "name", "grade", "cycle", "birth_date")
    ordering = ("name",)
