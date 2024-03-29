# Generated by Django 3.2.23 on 2024-01-22 16:41

from django.db import migrations


def set_project_attribute_on_script(apps, schema_editor):
    Script = apps.get_model("recordings", "Script")

    for script in Script.objects.filter(projects__isnull=False):
        if not script.project:
            script.project = script.projects.first()
            script.save()


class Migration(migrations.Migration):
    dependencies = [
        ("recordings", "0015_auto_20240122_1639"),
    ]

    operations = [migrations.RunPython(set_project_attribute_on_script)]
