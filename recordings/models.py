from django.db import models
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.contrib.postgres.constraints import ExclusionConstraint
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.html import format_html
from django.utils.translation import trans_real
from django.utils.timezone import localtime
from .fields import CustomFileField
import uuid
import os


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

    @property
    def age(self):
        """
        Speakers age at the time of the recording session
        """
        dob = self.dateOfBirth

        if self.project and dob:
            date = self.project.session.lower
            return (
                date.year - dob.year - ((date.month, date.day) < (dob.month, dob.day))
            )

    @property
    def recorded(self):
        try:
            return self.project.script.recprompts.filter(recording__gt="").exists()
        except:
            return False

    def get_absolute_url(self):
        return f"/api/speakers/{self.pk}/"

    def __str__(self):
        return self.name


class Format(models.Model):
    frameSize = models.PositiveSmallIntegerField(default=3)
    sampleRate = models.PositiveIntegerField(default=48000)
    bigEndian = models.BooleanField(default=True)
    sampleSizeInBits = models.PositiveSmallIntegerField(default=24)

    def __str__(self):
        return f"{self.sampleRate} Hz / {self.sampleSizeInBits} bit / {self.channels.count()} ch"


class Channel(models.Model):
    Format = models.ForeignKey(
        Format, related_name="channels", on_delete=models.PROTECT
    )
    index = models.PositiveSmallIntegerField(
        default=0, help_text="Channel index starting from 0"
    )
    microphone = models.ForeignKey("recordings.Microphone", on_delete=models.PROTECT)

    class Meta:
        unique_together = ("Format", "index")

    def __str__(self):
        return f"{self.index}. {self.microphone.model}"


class GetDefaultMixin:
    @classmethod
    def get_default_pk(cls):
        obj = cls.objects.filter(default=True).first()
        if obj:
            return obj.pk


class RecordingConfig(models.Model, GetDefaultMixin):
    CAPTURE_SCOPE_CHOICES = (("S", "SESSION"), ("I", "ITEM"))
    MODE_CHOICES = (("m", "manual"), ("p", "autoprogress"), ("r", "autorecording"))

    url = models.CharField(max_length=64, default="RECS/")
    Format = models.ForeignKey(Format, on_delete=models.PROTECT, verbose_name="Format")
    captureScope = models.CharField(
        max_length=1, choices=CAPTURE_SCOPE_CHOICES, default="S"
    )
    mode = models.CharField(max_length=1, default="r", choices=MODE_CHOICES)
    progressToNextUnrecorded = models.BooleanField(default=True)
    default = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["default"],
                condition=Q(default=True),
                name="unique_%(class)s_default",
            )
        ]

    def __str__(self):
        return f"{self.url} - {self.Format}"


class MixerName(models.Model, GetDefaultMixin):
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
    interfaceName = models.CharField(max_length=128, null=True, blank=True)


class PlaybackMixerName(MixerName):
    pass


class FileModelQuerySet(models.QuerySet):
    """
    Remove the file from S3 storage
    """

    def delete(self, *args, **kwargs):
        for obj in self:
            for field in obj._meta.fields:
                if field.__class__ == CustomFileField:
                    getattr(obj, field.name).delete()

        super(FileModelQuerySet, self).delete(*args, **kwargs)


class Equipment(models.Model, GetDefaultMixin):
    model = models.CharField(max_length=128)
    manual = CustomFileField(
        upload_to="documentation/manuals", validators=[FileExtensionValidator(["pdf"])]
    )
    default = models.BooleanField(default=False)

    objects = FileModelQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        if self.manual:
            self.manual.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.model

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=["default"],
                condition=Q(default=True),
                name="unique_%(class)s_default",
            )
        ]


class Microphone(Equipment):
    pass


class Soundcard(Equipment):
    pass


def upload_path(instance, filename):
    if isinstance(instance, Project):
        filename, extension = os.path.splitext(filename)
        filename = f"{instance.speaker.name} release form{extension}"
    else:
        instance = instance.script.project

    date = instance.session.lower
    return f"{date.strftime('%Y/%m/%d/PROJECT_ID_')}{instance.id}/{filename}"


class Project(models.Model):
    session = DateTimeRangeField()
    private = models.BooleanField(default=False)
    speaker = models.OneToOneField(Speaker, on_delete=models.PROTECT)
    script = models.OneToOneField(
        "recordings.Script", null=True, on_delete=models.PROTECT
    )
    RecordingConfiguration = models.ForeignKey(
        RecordingConfig,
        default=RecordingConfig.get_default_pk,
        on_delete=models.PROTECT,
    )
    recordingMixerName = models.ForeignKey(
        RecordingMixerName,
        default=RecordingMixerName.get_default_pk,
        on_delete=models.PROTECT,
    )
    playbackMixerName = models.ForeignKey(
        PlaybackMixerName,
        default=PlaybackMixerName.get_default_pk,
        on_delete=models.PROTECT,
    )
    no_show = models.BooleanField(default=False)
    release_form = CustomFileField(
        upload_to=upload_path,
        validators=[FileExtensionValidator(["pdf"])],
        null=True,
        blank=True,
    )
    microphone = models.ForeignKey(
        Microphone,
        default=Microphone.get_default_pk,
        on_delete=models.PROTECT,
    )
    soundcard = models.ForeignKey(
        Soundcard,
        default=Soundcard.get_default_pk,
        on_delete=models.PROTECT,
    )
    archive = models.ForeignKey(
        "reports.Archive", related_name="projects", on_delete=models.PROTECT, null=True
    )

    objects = FileModelQuerySet.as_manager()

    class Meta:
        ordering = ("session__startswith",)
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_sessions",
                expressions=[("session", RangeOperators.OVERLAPS)],
            ),
        ]

    def validate_unique(self, exclude=None):
        if self.session:
            projects = Project.objects.filter(session__overlap=self.session)
            if projects.exclude(id=self.id).exists():
                raise ValidationError("That session is already booked")
        return super().validate_unique()

    def get_absolute_url(self):
        return f"/api/projects/{self.pk}/"

    def delete(self, *args, **kwargs):
        if self.release_form:
            self.release_form.delete()
        super(Project, self).delete(*args, **kwargs)

    @property
    def name(self):
        return self.__str__().replace(":", "-")

    def __str__(self):
        if self.session and self.speaker:
            dt = localtime(self.session.lower)
            return f"{dt.strftime('%Y-%m-%d %H:%M')} - {self.speaker}"
        return super().__str__()


class Script(models.Model):
    LANGUAGE_CHOICES = trans_real.get_languages().items()
    language = models.CharField(max_length=7, choices=LANGUAGE_CHOICES, default="en")

    class Meta:
        ordering = ("id",)

    def get_absolute_url(self):
        return f"/api/scripts/{self.pk}/"

    def __str__(self):
        return f"script_{self.pk}"

    def get_iso_string(self):
        return f"{self.get_language_display().upper()}_2_{self.language}"


class RecPrompt(models.Model):
    class InstructionChoices(models.TextChoices):
        FAST = "0", "fast"
        ANGRY = "1", "angry"
        HIGH_PITCH = "2", "high-pitch"
        LOW_PITCH = "3", "low-pitch"
        SLOW = "4", "slow"
        HAPPY = "5", "happy"
        SAD = "6", "sad"
        WHISPER = "7", "whisper"

    script = models.ForeignKey(
        Script,
        null=True,
        blank=True,
        related_name="recprompts",
        on_delete=models.PROTECT,
    )
    recinstructions = models.CharField(
        max_length=1, default="", blank=True, choices=InstructionChoices.choices
    )
    mediaitem = models.CharField(unique=True, max_length=255)
    finalsilence = models.PositiveIntegerField(
        default=4000, help_text="Duration in milliseconds"
    )
    recording = CustomFileField(
        upload_to=upload_path,
        validators=[FileExtensionValidator(["wav"])],
        null=True,
        blank=True,
    )
    filesize = models.PositiveIntegerField(null=True, blank=True, editable=False)

    objects = FileModelQuerySet.as_manager()

    @property
    def _recording(self):
        if self and self.recording:
            basename = os.path.basename(self.recording.name)
            url = self.recording.url

            return format_html(
                f'<a href="{url}">{basename}</a></br><audio controls src="{url}"></audio>'
            )
        return ""

    @property
    def _filesize(self):
        if self.filesize:
            return filesizeformat(self.filesize)
        return ""

    def get_absolute_url(self):
        return f"/api/recordings/{self.pk}/"

    def save(self, *args, **kwargs):
        if self.recording:
            self.filesize = self.recording.size
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.recording:
            self.recording.delete()
        super(RecPrompt, self).delete(*args, **kwargs)

    def __str__(self):
        return self.mediaitem

    def construct_filename(self):
        speaker = self.script.project.speaker
        return f"LMC_{self.script.get_iso_string()}_{speaker.pk}_{speaker.sex}_0_0_{self.pk}.wav"

    class Meta:
        ordering = ("id",)
