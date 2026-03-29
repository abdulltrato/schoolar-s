from django.test import TestCase

from apps.curriculum.models import CurriculumArea
from apps.learning.serializers import CourseSerializer
from apps.school.models import Grade, School


class CourseCurriculumAreaTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(code="ESC-COURSE", name="Escola Curso", tenant_id="tenant-course")
        self.grade = Grade.objects.create(number=1, cycle=1)
        self.area = CurriculumArea.objects.create(name="Área 1", tenant_id=self.school.tenant_id)

    def _course_payload(self, extra=None):
        payload = {
            "school": self.school.id,
            "title": "Curso transversal",
            "description": "Descrição",
            "modality": "online",
        }
        if extra:
            payload.update(extra)
        return payload

    def test_requer_areas_curriculares(self):
        serializer = CourseSerializer(data=self._course_payload())
        self.assertFalse(serializer.is_valid())
        self.assertIn("curriculum_area_ids", serializer.errors)

    def test_atribui_areas_na_criacao(self):
        serializer = CourseSerializer(data=self._course_payload({"curriculum_area_ids": [self.area.id]}))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        course = serializer.save()
        self.assertEqual(list(course.curriculum_areas.all()), [self.area])
