# Importa o modelo de aluno principal para exposição pelo pacote.
from .student import Student
# Importa o modelo que armazena a proficiência do aluno em cada competência.
from .student_competency import StudentCompetency
# Importa o modelo de encarregado/guardião do aluno.
from .guardian import Guardian
# Importa a relação entre alunos e encarregados.
from .student_guardian import StudentGuardian
# Importa os resultados de aprendizagem dos alunos.
from .student_outcome import StudentOutcome

# Define quais classes ficam visíveis ao usar `from apps.academic import *`.
__all__ = [
    "Student",
    "StudentCompetency",
    "Guardian",
    "StudentGuardian",
    "StudentOutcome",
]
