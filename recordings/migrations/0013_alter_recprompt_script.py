# Generated by Django 3.2.23 on 2024-01-22 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0012_rename_recording_recprompt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recprompt',
            name='script',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recprompts', to='recordings.script'),
        ),
    ]