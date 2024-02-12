from rest_framework import serializers
from .models import *


class FormatSerializer(serializers.ModelSerializer):
    sampleRate = serializers.FloatField()

    class Meta:
        model = Format
        exclude = ("id",)


class RecordingConfigSerializer(serializers.ModelSerializer):
    Format = FormatSerializer()
    captureScope = serializers.SerializerMethodField()

    def get_captureScope(self, instance):
        return instance.get_captureScope_display()

    class Meta:
        model = RecordingConfig
        exclude = ("id",)


class ProjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="__str__")
    recordingMixerName = serializers.SerializerMethodField()
    playbackMixerName = serializers.SerializerMethodField()
    RecordingConfiguration = RecordingConfigSerializer()
    PromptConfiguration = serializers.SerializerMethodField()
    Speakers = serializers.SerializerMethodField()

    def get_recordingMixerName(self, instance):
        return {
            "recordingMixerName": instance.recordingMixerName.name,
            "attrs": {"providerId": instance.recordingMixerName.providerId},
        }

    def get_playbackMixerName(self, instance):
        return {
            "playbackMixerName": instance.playbackMixerName.name,
            "attrs": {"providerId": instance.playbackMixerName.providerId},
        }

    def get_PromptConfiguration(self, instance):
        return {
            "promptsUrl": f"{instance.script.pk}_script.xml",
            "InstructionsFont": {"family": "SansSerif"},
            "PromptFont": {"family": "SansSerif"},
            "DescriptionFont": {"family": "SansSerif"},
            "automaticPromptPlay": "false",
            "PromptBeep": {"beepGainRatio": "1.0"},
        }

    def get_Speakers(self, instance):
        return {"speakersUrl": f"{instance.speaker.pk}_speakers.xml"}

    class Meta:
        model = Project
        fields = (
            "name",
            "recordingMixerName",
            "playbackMixerName",
            "RecordingConfiguration",
            "PromptConfiguration",
            "Speakers",
        )


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


class RecPromptSerializer(serializers.ModelSerializer):
    recprompt = serializers.SerializerMethodField()

    class Meta:
        model = RecPrompt
        exclude = ("script", "mediaitem")

    def get_recprompt(self, instance):
        return {
            "mediaitem": {
                "mediaitem": instance.mediaitem,
                "attrs": {"languageISO639code": "en"},
            }
        }


class RecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecPrompt
        fields = "__all__"


class ScriptSerializer(serializers.ModelSerializer):
    script = serializers.SerializerMethodField()

    def get_recordings(self, instance):
        data = RecPromptSerializer(instance.recprompts.all(), many=True).data
        recordings = []

        for recording in data:
            recordings.append(
                {
                    "recprompt": recording["recprompt"],
                    "attrs": {
                        "finalsilence": str(recording["finalsilence"]),
                        "itemcode": f"{recording['id']:010}",
                    },
                }
            )
        return recordings

    def get_script(self, instance):
        return {
            "recordingscript": {
                "section": {
                    "section": self.get_recordings(instance),
                    "attrs": {
                        "name": f"script_{instance.id}",
                        "promptphase": "recording",
                        "speakerdisplay": "true",
                    },
                },
            },
            "attrs": {
                "id": f"script_{instance.id}",
            },
        }

    class Meta:
        model = Script
        exclude = ("id",)
