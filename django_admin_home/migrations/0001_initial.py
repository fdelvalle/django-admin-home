from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MenuFavorite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("menu_key", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="admin_home_favorites",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Menu favorite",
                "verbose_name_plural": "Menu favorites",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="MenuAccess",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("menu_key", models.CharField(max_length=255)),
                ("access_count", models.PositiveIntegerField(default=0)),
                ("last_access", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="admin_home_accesses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Menu access",
                "verbose_name_plural": "Menu accesses",
                "ordering": ["-access_count", "-last_access"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="menufavorite",
            unique_together={("user", "menu_key")},
        ),
        migrations.AlterUniqueTogether(
            name="menuaccess",
            unique_together={("user", "menu_key")},
        ),
    ]
