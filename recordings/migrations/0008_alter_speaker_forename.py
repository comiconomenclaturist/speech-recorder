# Generated by Django 3.2.23 on 2024-01-19 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0007_auto_20240117_2329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speaker',
            name='forename',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
