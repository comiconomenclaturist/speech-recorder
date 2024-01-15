from rest_framework import serializers
from .models import *


class ProjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="__str__")
    recordingMixerName = serializers.CharField(read_only=True)
    playbackMixerName = serializers.CharField(read_only=True)
    RecordingConfiguration = serializers.SerializerMethodField()
    PromptConfiguration = serializers.SerializerMethodField()
    Speakers = serializers.SerializerMethodField()

    def get_RecordingConfiguration(self, instance):
        return {
            "url": "RECS/",
            "Format": {"channels": "1", "frameSize": "2"},
            "captureScope": "SESSION",
        }

    def get_PromptConfiguration(self, instance):
        return {
            "promptsUrl": f"{instance.script}.xml",
            "InstructionsFont": {"family": "SansSerif"},
            "PromptFont": {"family": "SansSerif"},
            "DescriptionFont": {"family": "SansSerif"},
            "automaticPromptPlay": "false",
            "PromptBeep": {"beepGainRatio": "1.0"},
        }

    def get_Speakers(self, instance):
        return {"speakersUrl": f"speaker_{instance.speaker.pk}.xml"}

    class Meta:
        model = Project
        exclude = ("id", "session", "script", "speaker")


class SpeakerSerializer(serializers.ModelSerializer):
    sex = serializers.SerializerMethodField()
    informedConsents = serializers.CharField(default=None)

    def get_sex(self, obj):
        return obj.get_sex_display()

    def get_dateOfBirthString(self, obj):
        return f"{obj.dateOfBirth.strftime('%-d %b %Y')}"

    class Meta:
        model = Speaker
        exclude = ("email",)


class ScriptSerializer(serializers.ModelSerializer):
    recording = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Script
        exclude = ("speaker",)
