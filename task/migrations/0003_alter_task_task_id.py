# Generated by Django 4.2.13 on 2024-06-12 11:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("task", "0002_alter_task_task_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="task_id",
            field=models.CharField(
                default="", editable=False, max_length=30, unique=True
            ),
        ),
    ]
