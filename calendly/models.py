from django.db import models
from recordings.models import Script


class CalendlyForm(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=127)
    private = models.BooleanField()
    language = models.CharField(
        max_length=7, choices=Script.LANGUAGE_CHOICES, default="en"
    )

    def __str__(self):
        return self.name
