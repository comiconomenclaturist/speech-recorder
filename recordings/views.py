from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.utils.timezone import now
from django.db import transaction
from psycopg2.extras import DateTimeTZRange
from urllib.parse import urlparse
from speech_recording import settings
from .models import *
from .serializers import *
from .permissions import TypeFormPermission, CalendlyPermission
from .renderers import *
import json
import requests


class ProjectsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    renderer_classes = (ProjectXMLRenderer,)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get("pk")

        if pk == "next":
            obj = queryset.filter(session__startswith__gte=now()).first()
        else:
            try:
                obj = queryset.get(pk=pk)
            except:
                raise Http404

        if obj:
            self.check_object_permissions(self.request, obj)
            return obj

        raise Http404


class SpeakersViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    renderer_classes = (SpeakerXMLRenderer,)


class ScriptsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer
    renderer_classes = (ScriptXMLRenderer,)


def calendly(url):
    url = urlparse(url)
    url = f"https://api.calendly.com/{url.path}"

    r = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {settings.env('CALENDLY_TOKEN')}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    if r.status_code == 200:
        return json.loads(r.text)
    raise Exception(r)


class CreateProjectView(generics.CreateAPIView):
    permission_classes = [TypeFormPermission]

    @csrf_exempt
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data

        if data["event_type"] == "form_response":
            project = Project()
            speaker = Speaker()

            for answer in data["form_response"]["answers"]:
                if answer["field"]["id"] == "LwvCDF97Z3oh":
                    speaker.sex = answer["choice"]["label"][0]
                elif answer["field"]["id"] == "PtsHxrWJV6UL":
                    speaker.dateOfBirth = answer["date"]
                elif answer["field"]["id"] == "R3boiK7GwVaq":
                    speaker.accent = answer["choice"]["label"]
                elif answer["field"]["id"] == "ntwEuuLyrVpH":
                    invitee = calendly(answer["url"])
                    speaker.name = invitee["resource"]["name"]
                    speaker.email = invitee["resource"]["email"]

                    event = calendly(invitee["resource"]["event"])
                    project.session = DateTimeTZRange(
                        event["resource"]["start_time"],
                        event["resource"]["end_time"],
                    )

            speaker.save()
            project.speaker = speaker
            project.RecordingConfiguration = RecordingConfig.objects.first()
            project.recordingMixerName = RecordingMixerName.objects.filter(
                default=True
            ).first()
            project.playbackMixerName = PlaybackMixerName.objects.filter(
                default=True
            ).first()
            project.script = Script.objects.filter(project__isnull=True).first()
            project.save()

        return Response({}, status=200)


class CalendlyWebhookView(generics.CreateAPIView):
    permission_classes = [CalendlyPermission]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        data = request.data

        with open("/tmp/test.txt", "a") as f:
            f.write(data + "\n")
            f.write("*" * 40)
            f.write("\n")

        # if data["event"] == "invitee.created":
        #     data["payload"]["scheduled_event"]["start_time"]
        #     data["payload"]["scheduled_event"]["end_time"]

        return Response({}, status=200)
