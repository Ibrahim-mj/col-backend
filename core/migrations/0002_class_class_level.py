# Generated by Django 5.0.4 on 2024-06-26 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="class",
            name="class_level",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
