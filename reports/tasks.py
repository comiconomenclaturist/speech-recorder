from django.core.files.storage import default_storage
from psycopg2.extras import DateTimeTZRange
from recordings.models import Project
from celery import shared_task
from zipfile import ZipFile
import tempfile
import os


def write_line(file, text):
    file.write(f"{text}\n".encode("utf-8"))


@shared_task(name="Create archive")
def create_archive(start, end):
    date_range = DateTimeTZRange(start, end)
    projects = Project.objects.filter(session__contained_by=date_range)

    with tempfile.NamedTemporaryFile(suffix="zip") as tmp:
        with ZipFile(tmp, "w") as zf:
            zf.mkdir("DOC")

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

        default_storage.save(
            f"ARCHIVE/{projects.first().session.lower.strftime('%Y/%B_%Y.zip')}", tmp
        )
