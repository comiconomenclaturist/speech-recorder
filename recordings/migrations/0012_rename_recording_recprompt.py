# Generated by Django 3.2.23 on 2024-01-22 12:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0011_merge_20240122_1024'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Recording',
            new_name='RecPrompt',
        ),
    ]
