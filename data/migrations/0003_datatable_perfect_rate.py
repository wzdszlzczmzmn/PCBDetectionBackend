# Generated by Django 4.2.13 on 2024-06-08 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_rename_line_datatable_line_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatable',
            name='perfect_rate',
            field=models.FloatField(default=0),
        ),
    ]
