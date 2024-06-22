# Generated by Django 5.0.4 on 2024-06-22 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_user_is_admin"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="adminprofile",
            name="phone_number",
        ),
        migrations.RemoveField(
            model_name="studentprofile",
            name="phone_number",
        ),
        migrations.RemoveField(
            model_name="tutorprofile",
            name="phone_number",
        ),
        migrations.AddField(
            model_name="user",
            name="phone_number",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
