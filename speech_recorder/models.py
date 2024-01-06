from django.db import models
import uuid


class Speaker(models.Model):
    SEX_CHOICES = (
        ("M", "MALE"),
        ("F", "FEMALE"),
        ("O", "OTHER"),
    )
    dob = models.DateField(verbose_name="Date of birth")
    forename = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    registered = models.DateTimeField(auto_now_add=True)
    sex = models.CharField(choices=SEX_CHOICES, max_length=1)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, default="", blank=True)
    accent = models.CharField(max_length=64, default="", blank=True)

    def __str__(self):
        return f"{self.forename} {self.name}"


class Format(models.Model):
    channels = models.PositiveSmallIntegerField()
    frame_size = models.PositiveSmallIntegerField()


class RecordingConfig(models.Model):
    url = models.CharField(max_length=64)
    fmt = models.ForeignKey(Format, on_delete=models.PROTECT)


class InstructionsFont(models.Model):
    def family(self):
        return "SansSerif"


class PromptConfig(models.Model):
    prompts_url = models.CharField(max_length=64)
    instructions_font = models.ForeignKey(InstructionsFont, on_delete=models.PROTECT)


class Project(models.Model):
    name = models.CharField(max_length=64)
    recording_mixer_name = models.CharField(max_length=64)
    playback_mixer_name = models.CharField(max_length=64)
    recording_config = models.ForeignKey(RecordingConfig, on_delete=models.PROTECT)
    prompt_config = models.ForeignKey(PromptConfig, on_delete=models.PROTECT)
