from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("academic", "0010_student_document_names"),
        ("school", "0008_alter_teacher_options_alter_teacherspecialty_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="enrollment",
            name="enrollment_fee",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Taxa de matrícula"),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="monthly_fee",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Mensalidade"),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="monthly_fee_end",
            field=models.DateField(blank=True, null=True, verbose_name="Fim cobrança mensalidade"),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="monthly_fee_start",
            field=models.DateField(blank=True, null=True, verbose_name="Início cobrança mensalidade"),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="exam_fee",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Taxa de exame"),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="exam_recurrence_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="Taxa de exame de recorrência",
            ),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="exam_special_fee",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=10, verbose_name="Taxa de exame especial"
            ),
        ),
        migrations.CreateModel(
            name="PaymentPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Atualizado em")),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name="Eliminado em")),
                ("code", models.CharField(blank=True, max_length=30, verbose_name="Código")),
                ("tenant_id", models.CharField(blank=True, max_length=50, verbose_name="Tenant")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("enrollment_fee", "Taxa de matrícula"),
                            ("tuition_monthly", "Mensalidade"),
                            ("propina", "Propina"),
                            ("exam_regular", "Exame"),
                            ("exam_recurrence", "Exame de recorrência"),
                            ("exam_special", "Exame especial"),
                        ],
                        max_length=30,
                        verbose_name="Tipo",
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=180, verbose_name="Descrição")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Valor")),
                ("due_date", models.DateField(blank=True, null=True, verbose_name="Data de vencimento")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("scheduled", "Agendado"),
                            ("invoiced", "Faturado"),
                            ("paid", "Pago"),
                            ("cancelled", "Cancelado"),
                        ],
                        default="scheduled",
                        max_length=20,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_plans",
                        to="school.enrollment",
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="school.invoice",
                        verbose_name="Fatura",
                    ),
                ),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="school.school", verbose_name="Escola"
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="academic.student", verbose_name="Aluno"
                    ),
                ),
            ],
            options={
                "verbose_name": "Plano de pagamento",
                "verbose_name_plural": "Planos de pagamento",
                "ordering": ["due_date", "type"],
            },
        ),
    ]
