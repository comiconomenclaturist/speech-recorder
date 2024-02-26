from django.core.files.storage import default_storage
from psycopg2.extras import DateTimeTZRange
from recordings.models import Project
from celery import shared_task
from zipfile import ZipFile
from reports.models import *
import tempfile
import os


def write_line(file, text):
    file.write(f"{text}\n".encode("utf-8"))


@shared_task(name="Create archive")
def create_archive(start, end):
    projects = Project.objects.filter(
        session__contained_by=DateTimeTZRange(start, end),
        script__recprompts__recording__gt="",
        archive__isnull=True,
    ).distinct()

    archive_name = f"ARCHIVE/{projects.first().session.lower.strftime('%Y/Resonance Speech Database %B %Y.zip')}"

    if default_storage.exists(archive_name):
        with tempfile.NamedTemporaryFile(suffix=".zip") as tmp:
            with ZipFile(tmp, "w", allowZip64=True) as zf:
                with zf.open("TABLE/SPEAKER.TXT", "w") as file:
                    write_line(file, "SCD\tSEX\tAGE\tACC")

                    for project in projects:
                        speaker = project.speaker
                        write_line(
                            file,
                            f"{speaker.pk}\t{speaker.sex}\t{speaker.age}\t{speaker.accent}",
                        )
                for project in projects:
                    speaker = f"DATA/CHANNEL0/WAVE/SPEAKER{project.speaker.pk}"
                    script = f"DATA/CHANNEL0/SCRIPT/0_{project.speaker.pk}_0.TXT"
                    recprompts = project.script.recprompts.filter(recording__gt="")

                    with zf.open(script, "w") as file:
                        for prompt in recprompts:
                            write_line(file, f"0_{project.speaker.pk}_{prompt.pk}")
                            write_line(file, f"\t{prompt.mediaitem}\n")

                    for prompt in recprompts:
                        filename = f"0_{project.speaker.pk}_0_{prompt.pk}.wav"
                        filepath = os.path.join(speaker, filename)
                        zf.writestr(filepath, prompt.recording.file.open().read())
                description = Description.objects.first()

                with zf.open(f"DOC/{description.name}.TXT", "w") as file:
                    write_line(file, f"{description.name}\n")
                    write_line(file, "Location:\n")
                    write_line(file, f"{description.location}\n")
                    write_line(file, "Equipment:\n")
                    write_line(file, f"{description.equipment}\n")
                    write_line(file, "Date range:\n")
                    write_line(
                        file,
                        f"{projects.first().session.lower} to {projects.last().session.upper}",
                    )

            default_storage.save(archive_name, tmp)

            archive, created = Archive.objects.get_or_create(
                description=Description.objects.first(), file=archive_name
            )
            projects.update(archive=archive)

            return f"{projects.count()} projects archived to {archive_name}"
