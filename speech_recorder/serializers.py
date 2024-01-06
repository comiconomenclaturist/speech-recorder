from rest_framework import serializers
from .models import Speaker


class SpeakerSerializer(serializers.ModelSerializer):
    personId = serializers.IntegerField(source="id")
    dateOfBirth = serializers.DateField(source="dob")
    sex = serializers.SerializerMethodField()
    informedConsents = serializers.CharField(default=None)
    dateOfBirthString = serializers.SerializerMethodField()

    def get_sex(self, obj):
        return obj.get_sex_display()

    def get_dateOfBirthString(self, obj):
        return f"{obj.dob.strftime('%-d %b %Y')}"

    class Meta:
        model = Speaker
        exclude = ("id", "dob")
