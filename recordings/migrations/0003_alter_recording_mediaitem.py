# Generated by Django 3.2.23 on 2024-01-17 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0002_alter_speaker_dateofbirth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recording',
            name='mediaitem',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
