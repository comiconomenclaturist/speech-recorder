# Generated by Django 3.2.23 on 2024-01-22 22:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0020_auto_20240122_2233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='script',
            name='project',
        ),
        migrations.AlterField(
            model_name='project',
            name='script',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='recordings.script'),
        ),
    ]
