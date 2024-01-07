from django.db import models
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.contrib.postgres.constraints import ExclusionConstraint
from speech_recorder.models import Speaker


class Booking(models.Model):
    session = DateTimeRangeField()
    speaker = models.ForeignKey(Speaker, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_sessions",
                expressions=[("session", RangeOperators.OVERLAPS)],
            ),
        ]

    def __str__(self):
        return f"{self.session.lower.strftime('%Y/%m/%d %H:%M')} - {self.speaker}"
