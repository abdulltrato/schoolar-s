from django.db import migrations, models


class Migration(migrations.Migration):
    """Adiciona URL de avatar ao perfil do utilizador."""

    dependencies = [
        ("school", "0011_paymentplan_usuario_alter_paymentplan_code_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="avatar_url",
            field=models.URLField(blank=True, max_length=500, verbose_name="Avatar"),
        ),
    ]
