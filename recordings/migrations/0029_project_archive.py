# Generated by Django 3.2.23 on 2024-02-19 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
        ('recordings', '0028_project_soundcard'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='archive',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='reports.archive'),
        ),
    ]
