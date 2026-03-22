from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("curriculo", "0003_alter_competencia_options_and_more"),
        ("escola", "0004_fase1_estrutura_academica"),
        ("avaliacao", "0003_alter_avaliacao_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="avaliacao",
            name="alocacao_docente",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="escola.alocacaodocente",
                verbose_name="Alocação Docente",
            ),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="competencia",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="curriculo.competencia",
                verbose_name="Competência",
            ),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="nota",
            field=models.DecimalField(
                blank=True,
                decimal_places=1,
                max_digits=4,
                null=True,
                verbose_name="Nota",
            ),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("acs", "ACS"),
                    ("acp", "ACP"),
                    ("trabalho_individual", "Trabalho Individual"),
                    ("trabalho_grupo", "Trabalho em Grupo"),
                    ("teste", "Teste"),
                    ("exame", "Exame"),
                    ("diagnostica", "Diagnóstica"),
                    ("formativa", "Formativa"),
                    ("sumativa", "Sumativa"),
                    ("outra", "Outra"),
                ],
                max_length=30,
                verbose_name="Tipo",
            ),
        ),
    ]
