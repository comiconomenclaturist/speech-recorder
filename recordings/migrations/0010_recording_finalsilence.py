# Generated by Django 3.2.23 on 2024-01-20 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0009_remove_speaker_forename'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='finalsilence',
            field=models.PositiveIntegerField(default=4000),
        ),
    ]