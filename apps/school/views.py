from core.viewsets import RobustModelViewSet

from .models import (
    AcademicYear,
    Classroom,
    Enrollment,
    Grade,
    GradeSubject,
    ManagementAssignment,
    School,
    Teacher,
    TeachingAssignment,
)
from .serializers import (
    AcademicYearSerializer,
    ClassroomSerializer,
    EnrollmentSerializer,
    GradeSerializer,
    GradeSubjectSerializer,
    ManagementAssignmentSerializer,
    SchoolSerializer,
    TeacherSerializer,
    TeachingAssignmentSerializer,
)


class AcademicYearViewSet(RobustModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    search_fields = ("code",)
    ordering_fields = ("id", "code", "start_date", "end_date", "active")
    ordering = ("-code",)


class GradeViewSet(RobustModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    search_fields = ("number", "name")
    ordering_fields = ("id", "number", "cycle", "name")
    ordering = ("number",)


class SchoolViewSet(RobustModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    search_fields = ("code", "name", "district", "province")
    ordering_fields = ("id", "code", "name", "district", "province")
    ordering = ("name",)


class TeacherViewSet(RobustModelViewSet):
    queryset = Teacher.objects.select_related("school").all()
    serializer_class = TeacherSerializer
    search_fields = ("name", "specialty", "user__username", "school__name")
    ordering_fields = ("id", "name", "specialty", "school__name")
    ordering = ("name",)


class ClassroomViewSet(RobustModelViewSet):
    queryset = Classroom.objects.select_related("school", "grade", "academic_year", "lead_teacher").all()
    serializer_class = ClassroomSerializer
    search_fields = ("name", "academic_year__code", "grade__name", "lead_teacher__name", "school__name")
    ordering_fields = ("id", "name", "cycle", "academic_year__code", "grade__number", "school__name")
    ordering = ("academic_year__code", "grade__number", "name")


class GradeSubjectViewSet(RobustModelViewSet):
    queryset = GradeSubject.objects.select_related("academic_year", "grade", "subject").all()
    serializer_class = GradeSubjectSerializer
    search_fields = ("academic_year__code", "grade__name", "subject__name")
    ordering_fields = ("id", "academic_year__code", "grade__number", "subject__name")
    ordering = ("academic_year__code", "grade__number", "subject__name")


class TeachingAssignmentViewSet(RobustModelViewSet):
    queryset = TeachingAssignment.objects.select_related(
        "teacher",
        "teacher__school",
        "classroom",
        "classroom__school",
        "classroom__academic_year",
        "classroom__grade",
        "grade_subject",
        "grade_subject__subject",
    ).all()
    serializer_class = TeachingAssignmentSerializer
    search_fields = ("teacher__name", "classroom__name", "grade_subject__subject__name", "classroom__school__name")
    ordering_fields = ("id", "teacher__name", "classroom__name", "grade_subject__subject__name")
    ordering = ("classroom__academic_year__code", "classroom__grade__number", "classroom__name")


class EnrollmentViewSet(RobustModelViewSet):
    queryset = Enrollment.objects.select_related(
        "student",
        "classroom",
        "classroom__school",
        "classroom__academic_year",
        "classroom__grade",
    ).all()
    serializer_class = EnrollmentSerializer
    search_fields = ("student__name", "classroom__name", "classroom__academic_year__code", "classroom__school__name")
    ordering_fields = ("id", "enrollment_date", "student__name", "classroom__name")
    ordering = ("-enrollment_date",)


class ManagementAssignmentViewSet(RobustModelViewSet):
    queryset = ManagementAssignment.objects.select_related(
        "teacher",
        "teacher__school",
        "school",
        "academic_year",
        "grade",
        "classroom",
    ).all()
    serializer_class = ManagementAssignmentSerializer
    search_fields = ("teacher__name", "school__name", "role", "academic_year__code")
    ordering_fields = ("id", "teacher__name", "school__name", "role", "academic_year__code")
    ordering = ("academic_year__code", "school__name", "role")
