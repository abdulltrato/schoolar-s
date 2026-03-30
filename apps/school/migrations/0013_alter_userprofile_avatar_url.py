from django.db import migrations, models


class Migration(migrations.Migration):
    """Permite armazenar data URLs longas no avatar."""

    dependencies = [
        ("school", "0012_userprofile_avatar_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="avatar_url",
            field=models.TextField(blank=True, verbose_name="Avatar"),
        ),
    ]
