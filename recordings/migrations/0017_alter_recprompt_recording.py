# Generated by Django 3.2.23 on 2024-01-22 17:16

from django.db import migrations, models
import recordings.models


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0016_auto_20240122_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recprompt',
            name='recording',
            field=models.FileField(blank=True, null=True, upload_to=recordings.models.upload_path),
        ),
    ]
