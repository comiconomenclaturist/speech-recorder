# Generated by Django 3.2.23 on 2024-01-17 23:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0006_alter_speaker_dateofbirth'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recordingconfig',
            old_name='fmt',
            new_name='Format',
        ),
        migrations.AddField(
            model_name='project',
            name='RecordingConfiguration',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='recordings.recordingconfig'),
        ),
        migrations.AddField(
            model_name='recordingconfig',
            name='captureScope',
            field=models.CharField(choices=[('S', 'SESSION'), ('I', 'ITEM')], default='S', max_length=1),
        ),
        migrations.AlterField(
            model_name='recordingconfig',
            name='url',
            field=models.CharField(default='RECS/', max_length=64),
        ),
    ]
