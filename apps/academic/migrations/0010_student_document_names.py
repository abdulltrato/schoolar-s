from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academic", "0009_student_cycle_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="identification_document_name",
            field=models.CharField(
                blank=True,
                help_text="Nome amigável do ficheiro enviado (ex.: BI do aluno).",
                max_length=150,
                null=True,
                verbose_name="Nome do documento de identificação",
            ),
        ),
        migrations.AddField(
            model_name="student",
            name="previous_certificate_name",
            field=models.CharField(
                blank=True,
                help_text="Nome amigável do certificado ou declaração enviada.",
                max_length=150,
                null=True,
                verbose_name="Nome do certificado/declaração anterior",
            ),
        ),
    ]
