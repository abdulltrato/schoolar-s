from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0009_payment_plan_and_enrollment_fees"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="payment_type",
            field=models.CharField(
                choices=[
                    ("enrollment_fee", "Taxa de matrícula"),
                    ("tuition_monthly", "Mensalidade"),
                    ("propina", "Propina"),
                    ("exam_regular", "Exame"),
                    ("exam_recurrence", "Exame de recorrência"),
                    ("exam_special", "Exame especial"),
                    ("other", "Outro"),
                ],
                default="other",
                max_length=30,
                verbose_name="Tipo de pagamento",
            ),
        ),
    ]
