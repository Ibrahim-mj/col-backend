# Generated by Django 5.0.4 on 2025-04-21 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0012_user_paid_reg"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="auth_provider",
            field=models.CharField(
                choices=[("EMAIL", "email"), ("GOOGLE", "google")],
                default="EMAIL",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="user_type",
            field=models.CharField(
                choices=[
                    ("ADMIN", "Admin"),
                    ("TUTOR", "Tutor"),
                    ("STUDENT", "Student"),
                ],
                default="STUDENT",
                max_length=255,
            ),
        ),
    ]
