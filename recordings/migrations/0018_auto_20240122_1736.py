# Generated by Django 3.2.23 on 2024-01-22 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0017_alter_recprompt_recording'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='script',
        ),
        migrations.RemoveField(
            model_name='script',
            name='speaker',
        ),
    ]
