from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from psycopg2.extras import DateTimeTZRange
from urllib.parse import urlparse
from speech_recording import settings
from .models import *
from .serializers import *
from .permissions import CreateProjectPermission
from .renderers import SpeakerXMLRenderer, ScriptXMLRenderer
import json
import requests


class ProjectsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class SpeakersViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]
    queryset = Speaker.objects.filter(projects__session__startswith__gte=now())
    serializer_class = SpeakerSerializer
    renderer_classes = (SpeakerXMLRenderer,)


class ScriptsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]
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
    permission_classes = [CreateProjectPermission]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        data = request.data
        project = Project()
        speaker = Speaker()

        if data["event_type"] == "form_response":
            for answer in data["form_response"]["answers"]:
                if answer["field"]["id"] == "LwvCDF97Z3oh":
                    speaker.sex = answer["choice"]["label"][0]
                elif answer["field"]["id"] == "BFHvuavpm2QD":
                    speaker.dateOfBirth = answer["date"]
                elif answer["field"]["id"] == "R3boiK7GwVaq":
                    speaker.accent = answer["choice"]["label"]
                elif answer["field"]["id"] == "ntwEuuLyrVpH":
                    invitee = calendly(answer["url"])
                    speaker.forename = invitee["resource"]["first_name"]
                    speaker.name = invitee["resource"]["last_name"]
                    speaker.email = invitee["resource"]["email"]

                    event = calendly(invitee["resource"]["event"])
                    project.session = DateTimeTZRange(
                        event["resource"]["start_time"],
                        event["resource"]["end_time"],
                    )

            speaker.save()
            project.speaker = speaker
            project.save()

        return Response({}, status=200)
