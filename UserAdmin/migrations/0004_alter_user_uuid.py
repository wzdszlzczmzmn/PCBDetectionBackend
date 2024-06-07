# Generated by Django 4.2.13 on 2024-06-06 12:36

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("UserAdmin", "0003_alter_user_uuid_alter_user_deviceuuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="UUID",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]
