# Generated by Django 5.0.4 on 2024-12-05 11:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0003_academicsession"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("course_code", models.CharField(max_length=10)),
                ("course_title", models.CharField(max_length=250)),
                (
                    "academic_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.academicsession",
                    ),
                ),
                (
                    "class_name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.class"
                    ),
                ),
                (
                    "tutor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("course_code", "class_name", "academic_session")},
            },
        ),
    ]
