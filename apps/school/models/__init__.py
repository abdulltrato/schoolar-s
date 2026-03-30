from .academic_year import AcademicYear, validate_academic_year_code
# Ano letivo e helper de validação de código.
from .cycle_grade import Cycle, Grade
# Ciclos de ensino e classes/anos.
from .school import School
# Entidade de escola/tenant.
from .teacher import Teacher, TeacherSpecialty
# Professores e suas especialidades.
from .classroom import Classroom
# Turmas/vínculos classe+ano letivo.
from .grade_subject import GradeSubject
# Disciplinas ofertadas por classe.
from .teaching_assignment import TeachingAssignment
# Alocação docente em disciplina/turma.
from .management_assignment import ManagementAssignment
# Cargos de gestão.
from .enrollment import Enrollment
# Matrículas de estudantes em turmas.
from .user_profile import UserProfile
# Perfil escolar associado ao usuário.
from .attendance import AttendanceRecord
# Registros de assiduidade.
from .announcement import Announcement
# Comunicados internos.
from .finance import Invoice, Payment
# Faturação e pagamentos.
from .audit import AuditEvent, AuditAlert
# Eventos e alertas de auditoria.
from .payment_plan import PaymentPlan
# Planos de pagamento.

__all__ = [
    "AcademicYear",
    "validate_academic_year_code",
    "Cycle",
    "Grade",
    "School",
    "Teacher",
    "TeacherSpecialty",
    "Classroom",
    "GradeSubject",
    "TeachingAssignment",
    "ManagementAssignment",
    "Enrollment",
    "UserProfile",
    "AttendanceRecord",
    "Announcement",
    "Invoice",
    "Payment",
    "AuditEvent",
    "AuditAlert",
    "PaymentPlan",
]
