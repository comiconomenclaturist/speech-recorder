# Generated by Django 3.2.23 on 2024-01-23 22:56

from django.db import migrations
import recordings.fields
import recordings.models


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0021_auto_20240122_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recprompt',
            name='recording',
            field=recordings.fields.RecordingField(blank=True, null=True, upload_to=recordings.models.upload_path),
        ),
    ]