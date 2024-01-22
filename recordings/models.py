from django.db import models
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.contrib.postgres.constraints import ExclusionConstraint
import uuid


class Speaker(models.Model):
    SEX_CHOICES = (
        ("M", "MALE"),
        ("F", "FEMALE"),
        ("O", "OTHER"),
    )
    personId = models.BigAutoField(primary_key=True)
    dateOfBirth = models.DateField(verbose_name="Date of birth")
    name = models.CharField(max_length=64)
    email = models.EmailField()
    registered = models.DateTimeField(auto_now_add=True)
    sex = models.CharField(choices=SEX_CHOICES, max_length=1)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, default="", blank=True)
    accent = models.CharField(max_length=64, default="", blank=True)

    def __str__(self):
        return self.name


class Script(models.Model):
    speaker = models.ForeignKey(
        Speaker, null=True, blank=True, on_delete=models.PROTECT
    )

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"script_{self.pk}"


class RecPrompt(models.Model):
    script = models.ForeignKey(
        Script,
        null=True,
        blank=True,
        related_name="recprompts",
        on_delete=models.PROTECT,
    )
    mediaitem = models.CharField(unique=True, max_length=255)
    finalsilence = models.PositiveIntegerField(default=4000)

    def __str__(self):
        return self.mediaitem


class Format(models.Model):
    channels = models.PositiveSmallIntegerField(default=1)
    frameSize = models.PositiveSmallIntegerField(default=3)
    sampleRate = models.PositiveIntegerField(default=48000)
    bigEndian = models.BooleanField(default=True)
    sampleSizeInBits = models.PositiveSmallIntegerField(default=24)

    def __str__(self):
        return f"{self.sampleRate} Hz / {self.sampleSizeInBits} bit"


class RecordingConfig(models.Model):
    CAPTURE_SCOPE_CHOICES = (("S", "SESSION"), ("I", "ITEM"))

    url = models.CharField(max_length=64, default="RECS/")
    Format = models.ForeignKey(Format, on_delete=models.PROTECT, verbose_name="Format")
    captureScope = models.CharField(
        max_length=1, choices=CAPTURE_SCOPE_CHOICES, default="S"
    )

    def __str__(self):
        return f"{self.url} - {self.Format}"


class MixerName(models.Model):
    name = models.CharField(max_length=64)
    providerId = models.CharField(max_length=128)
    default = models.BooleanField(default=False)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["default"],
                condition=models.Q(default=True),
                name="%(class)s_unique_default",
            )
        ]

    def __str__(self):
        return self.name


class RecordingMixerName(MixerName):
    pass


class PlaybackMixerName(MixerName):
    pass


class Project(models.Model):
    session = DateTimeRangeField()
    speaker = models.ForeignKey(
        Speaker, related_name="projects", on_delete=models.PROTECT
    )
    script = models.ForeignKey(Script, null=True, on_delete=models.PROTECT)
    RecordingConfiguration = models.ForeignKey(
        RecordingConfig, null=True, on_delete=models.PROTECT
    )
    recordingMixerName = models.ForeignKey(
        RecordingMixerName, null=True, on_delete=models.PROTECT
    )
    playbackMixerName = models.ForeignKey(
        PlaybackMixerName, null=True, on_delete=models.PROTECT
    )

    class Meta:
        ordering = ("session__startswith",)
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_sessions",
                expressions=[("session", RangeOperators.OVERLAPS)],
            ),
        ]

    def __str__(self):
        return f"{self.session.lower.strftime('%Y-%m-%d %H:%M')} - {self.speaker}"
