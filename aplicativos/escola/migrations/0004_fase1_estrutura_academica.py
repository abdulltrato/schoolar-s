from datetime import date

from django.db import migrations, models
import django.db.models.deletion


def popular_anos_letivos(apps, schema_editor):
    Turma = apps.get_model("escola", "Turma")
    AnoLetivo = apps.get_model("escola", "AnoLetivo")

    for turma in Turma.objects.exclude(ano_letivo_legado__isnull=True).exclude(ano_letivo_legado=""):
        codigo = turma.ano_letivo_legado
        try:
            ano_inicio, ano_fim = [int(valor) for valor in codigo.split("-")]
        except (TypeError, ValueError):
            continue

        ano_letivo, _ = AnoLetivo.objects.get_or_create(
            codigo=codigo,
            defaults={
                "data_inicio": date(ano_inicio, 2, 1),
                "data_fim": date(ano_fim, 12, 15),
                "ativo": False,
            },
        )
        turma.ano_letivo_id = ano_letivo.id
        turma.save(update_fields=["ano_letivo"])


class Migration(migrations.Migration):

    dependencies = [
        ("curriculo", "0003_alter_competencia_options_and_more"),
        ("escola", "0003_alter_matricula_options_alter_professor_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnoLetivo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=9, unique=True, verbose_name="Ano Letivo")),
                ("data_inicio", models.DateField(verbose_name="Data de Início")),
                ("data_fim", models.DateField(verbose_name="Data de Fim")),
                ("ativo", models.BooleanField(default=False, verbose_name="Ativo")),
            ],
            options={
                "verbose_name": "Ano Letivo",
                "verbose_name_plural": "Anos Letivos",
                "ordering": ["-codigo"],
            },
        ),
        migrations.CreateModel(
            name="Classe",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero", models.PositiveSmallIntegerField(unique=True, verbose_name="Classe")),
                ("ciclo", models.PositiveSmallIntegerField(verbose_name="Ciclo")),
                ("nome", models.CharField(blank=True, max_length=50, verbose_name="Nome")),
            ],
            options={
                "verbose_name": "Classe",
                "verbose_name_plural": "Classes",
                "ordering": ["numero"],
            },
        ),
        migrations.RenameField(
            model_name="turma",
            old_name="ano_letivo",
            new_name="ano_letivo_legado",
        ),
        migrations.AddField(
            model_name="turma",
            name="ano_letivo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="escola.anoletivo",
                verbose_name="Ano Letivo",
            ),
        ),
        migrations.AddField(
            model_name="turma",
            name="classe",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="escola.classe",
                verbose_name="Classe",
            ),
        ),
        migrations.AlterField(
            model_name="turma",
            name="professor_responsavel",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="escola.professor",
                verbose_name="Director de Turma",
            ),
        ),
        migrations.CreateModel(
            name="DisciplinaClasse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("carga_horaria_semanal", models.PositiveSmallIntegerField(default=0, verbose_name="Carga Horária Semanal")),
                (
                    "ano_letivo",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="escola.anoletivo", verbose_name="Ano Letivo"),
                ),
                (
                    "classe",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="escola.classe", verbose_name="Classe"),
                ),
                (
                    "disciplina",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="curriculo.disciplina", verbose_name="Disciplina"),
                ),
            ],
            options={
                "verbose_name": "Disciplina da Classe",
                "verbose_name_plural": "Disciplinas das Classes",
                "ordering": ["ano_letivo__codigo", "classe__numero", "disciplina__nome"],
                "unique_together": {("ano_letivo", "classe", "disciplina")},
            },
        ),
        migrations.CreateModel(
            name="AlocacaoDocente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "disciplina_classe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="escola.disciplinaclasse",
                        verbose_name="Disciplina da Classe",
                    ),
                ),
                (
                    "professor",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="escola.professor", verbose_name="Professor"),
                ),
                (
                    "turma",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="escola.turma", verbose_name="Turma"),
                ),
            ],
            options={
                "verbose_name": "Alocação Docente",
                "verbose_name_plural": "Alocações Docentes",
                "ordering": ["turma__ano_letivo__codigo", "turma__nome", "disciplina_classe__disciplina__nome"],
                "unique_together": {("turma", "disciplina_classe")},
            },
        ),
        migrations.RunPython(popular_anos_letivos, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="turma",
            name="ano_letivo_legado",
        ),
        migrations.AlterModelOptions(
            name="turma",
            options={
                "ordering": ["ano_letivo__codigo", "classe__numero", "nome"],
                "verbose_name": "Turma",
                "verbose_name_plural": "Turmas",
            },
        ),
        migrations.AlterUniqueTogether(
            name="turma",
            unique_together={("nome", "classe", "ano_letivo")},
        ),
    ]
