from datetime import date

from django.db import migrations, models
import django.db.models.deletion


def popular_anos_letivos(apps, schema_editor):
    Classroom = apps.get_model("school", "Classroom")
    AcademicYear = apps.get_model("school", "AcademicYear")

    for classroom in Classroom.objects.exclude(ano_letivo_legado__isnull=True).exclude(ano_letivo_legado=""):
        code = classroom.ano_letivo_legado
        try:
            ano_inicio, ano_fim = [int(valor) for valor in code.split("-")]
        except (TypeError, ValueError):
            continue

        academic_year, _ = AcademicYear.objects.get_or_create(
            code=code,
            defaults={
                "start_date": date(ano_inicio, 2, 1),
                "end_date": date(ano_fim, 12, 15),
                "active": False,
            },
        )
        classroom.ano_letivo_id = academic_year.id
        classroom.save(update_fields=["academic_year"])


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum", "0003_alter_competencia_options_and_more"),
        ("school", "0003_alter_matricula_options_alter_professor_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AcademicYear",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=9, unique=True, verbose_name="Ano Letivo")),
                ("start_date", models.DateField(verbose_name="Data de Início")),
                ("end_date", models.DateField(verbose_name="Data de Fim")),
                ("active", models.BooleanField(default=False, verbose_name="Ativo")),
            ],
            options={
                "verbose_name": "Ano Letivo",
                "verbose_name_plural": "Anos Letivos",
                "ordering": ["-code"],
            },
        ),
        migrations.CreateModel(
            name="Grade",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.PositiveSmallIntegerField(unique=True, verbose_name="Grade")),
                ("cycle", models.PositiveSmallIntegerField(verbose_name="Ciclo")),
                ("name", models.CharField(blank=True, max_length=50, verbose_name="Nome")),
            ],
            options={
                "verbose_name": "Grade",
                "verbose_name_plural": "Classes",
                "ordering": ["number"],
            },
        ),
        migrations.RenameField(
            model_name="classroom",
            old_name="academic_year",
            new_name="ano_letivo_legado",
        ),
        migrations.AddField(
            model_name="classroom",
            name="academic_year",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="school.anoletivo",
                verbose_name="Ano Letivo",
            ),
        ),
        migrations.AddField(
            model_name="classroom",
            name="grade",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="school.grade",
                verbose_name="Grade",
            ),
        ),
        migrations.AlterField(
            model_name="classroom",
            name="lead_teacher",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="school.teacher",
                verbose_name="Director de Classroom",
            ),
        ),
        migrations.CreateModel(
            name="GradeSubject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weekly_workload", models.PositiveSmallIntegerField(default=0, verbose_name="Carga Horária Semanal")),
                (
                    "academic_year",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="school.anoletivo", verbose_name="Ano Letivo"),
                ),
                (
                    "grade",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="school.grade", verbose_name="Grade"),
                ),
                (
                    "subject",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="curriculum.subject", verbose_name="Subject"),
                ),
            ],
            options={
                "verbose_name": "Subject da Grade",
                "verbose_name_plural": "Disciplinas das Classes",
                "ordering": ["ano_letivo__codigo", "classe__numero", "disciplina__nome"],
                "unique_together": {("academic_year", "grade", "subject")},
            },
        ),
        migrations.CreateModel(
            name="TeachingAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "grade_subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="school.disciplinaclasse",
                        verbose_name="Subject da Grade",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="school.teacher", verbose_name="Teacher"),
                ),
                (
                    "classroom",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="school.classroom", verbose_name="Classroom"),
                ),
            ],
            options={
                "verbose_name": "Alocação Docente",
                "verbose_name_plural": "Alocações Docentes",
                "ordering": ["turma__ano_letivo__codigo", "turma__nome", "disciplina_classe__disciplina__nome"],
                "unique_together": {("classroom", "grade_subject")},
            },
        ),
        migrations.RunPython(popular_anos_letivos, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="classroom",
            name="ano_letivo_legado",
        ),
        migrations.AlterModelOptions(
            name="classroom",
            options={
                "ordering": ["ano_letivo__codigo", "classe__numero", "name"],
                "verbose_name": "Classroom",
                "verbose_name_plural": "Turmas",
            },
        ),
        migrations.AlterUniqueTogether(
            name="classroom",
            unique_together={("name", "grade", "academic_year")},
        ),
    ]
