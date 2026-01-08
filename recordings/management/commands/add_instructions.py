from django.core.management.base import BaseCommand
from recordings.models import Script, RecPrompt


class Command(BaseCommand):
    help = "Add instructions to 25% of RecPrompts in unassigned Scripts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--language", type=str, default="en", help="Specify the language code"
        )

    def handle(self, *args, **options):
        language = options["language"]

        scripts = (
            Script.objects.filter(project__isnull=True, language=language)
            .exclude(recprompts__recinstructions__gt="")
            .distinct()
        )

        for script in scripts:
            percentage = -(-script.recprompts.count() // 4)  # Ceiling division for 25%
            choices = RecPrompt.InstructionChoices.choices
            recprompts = list(script.recprompts.order_by("?")[:percentage])
            for index, recprompt in enumerate(recprompts):
                recprompt.recinstructions = choices[index % len(choices)][0]

            RecPrompt.objects.bulk_update(recprompts, ["recinstructions"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated {scripts.count()} scripts recprompt instructions."
            )
        )
