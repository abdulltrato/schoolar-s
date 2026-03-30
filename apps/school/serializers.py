from .serializers_academic import AcademicYearSerializer, GradeSerializer, GradeSubjectSerializer
# Serializers para componentes acadêmicos.
from .serializers_school import SchoolSerializer, ClassroomSerializer, TeachingAssignmentSerializer
# Serializers de escola, turma e alocação docente.
from .serializers_enrollment import EnrollmentSerializer, EnrollmentSummarySerializer
# Serializers de matrículas.
from .serializers_management import ManagementAssignmentSerializer
# Serializers de cargos de gestão.
from .serializers_user import UserProfileSerializer, TeacherSerializer
# Serializers de perfis e professores.
from .serializers_attendance import AttendanceRecordSerializer
# Serializer de registros de assiduidade.
from .serializers_announcement import AnnouncementSerializer
# Serializer de comunicados.
from .serializers_finance import InvoiceSerializer, PaymentSerializer
# Serializers financeiros.
from .serializers_audit import AuditAlertSerializer, AuditEventSerializer
# Serializers de auditoria.

# Exporta todos para import fácil no restante do projeto.
__all__ = [
    "AcademicYearSerializer",
    "GradeSerializer",
    "GradeSubjectSerializer",
    "SchoolSerializer",
    "ClassroomSerializer",
    "TeachingAssignmentSerializer",
    "EnrollmentSerializer",
    "EnrollmentSummarySerializer",
    "ManagementAssignmentSerializer",
    "UserProfileSerializer",
    "TeacherSerializer",
    "AttendanceRecordSerializer",
    "AnnouncementSerializer",
    "InvoiceSerializer",
    "PaymentSerializer",
    "AuditAlertSerializer",
    "AuditEventSerializer",
]
