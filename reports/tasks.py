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
def create_archive(start, end, language):
    projects = Project.objects.filter(
        session__contained_by=DateTimeTZRange(start, end),
        script__recprompts__recording__gt="",
        script__language=language,
        archive__isnull=True,
    ).distinct()

    if projects:
        first = projects.first().session.lower
        last = projects.last().session.upper

        archive_name = f"ARCHIVE/{first.year}/Resonance Speech Database [{language.upper()}] {first.date()} - {last.date()}.zip"

        if not default_storage.exists(archive_name):
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
                                write_line(file, f"\t{prompt.mediaitem}")
                                write_line(
                                    file, f"\t{prompt.get_recinstructions_display()}\n"
                                )

                        for prompt in recprompts:
                            filename = prompt.construct_filename()
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
                updated = projects.update(archive=archive)

                return f"{updated} projects archived to {archive_name}"

        return "Archive with this name already exists"

    return "No eligible projects found for archiving"
