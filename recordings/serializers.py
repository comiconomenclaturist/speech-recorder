from rest_framework import serializers
from .models import *


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


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


class RecordingSerializer(serializers.Serializer):
    mediaitem = serializers.CharField()

    class Meta:
        model = Recording


class ScriptSerializer(serializers.ModelSerializer):
    recording = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Script
        exclude = ("speaker",)
