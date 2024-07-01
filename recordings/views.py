from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import filters
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.utils.timezone import now
from django.db import transaction
from dateutil.parser import parse
from psycopg2.extras import DateTimeTZRange
from calendly.client import Calendly
from speech_recording import settings
from .models import *
from .serializers import *
from .permissions import TypeFormPermission, CalendlyPermission
from .renderers import *


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


class CreateProjectView(generics.CreateAPIView):
    permission_classes = [TypeFormPermission | CalendlyPermission]

    @csrf_exempt
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data
        project = Project()
        speaker = Speaker()

        if data.get("event") == "invitee.created":
            PRIVATE_ID = settings.env("CALENDLY_PRIVATE_BOOKING_ID")
            payload = data["payload"]
            event = payload["scheduled_event"]

            if not payload["rescheduled"]:
                if event["event_type"].endswith(PRIVATE_ID):
                    for answer in payload["questions_and_answers"]:
                        if answer["question"] == "Gender":
                            speaker.sex = answer["answer"][0]
                        elif answer["question"] == "Date of Birth (DD/MM/YYYY)":
                            speaker.dateOfBirth = parse(answer["answer"], dayfirst=True)
                        elif answer["question"] == "Accent":
                            speaker.accent = answer["answer"]

                    speaker.name = " ".join(payload["name"].split())
                    speaker.email = payload["email"]

                    project.session = DateTimeTZRange(
                        event["start_time"], event["end_time"]
                    )
                    project.private = True

        elif data.get("event_type") == "form_response":

            for answer in data["form_response"]["answers"]:
                if answer["field"]["id"] == "LwvCDF97Z3oh":
                    speaker.sex = answer["choice"]["label"][0]

                elif answer["field"]["id"] == "PtsHxrWJV6UL":
                    speaker.dateOfBirth = answer["date"]

                elif answer["field"]["id"] == "R3boiK7GwVaq":
                    speaker.accent = answer["choice"]["label"]

                elif answer["field"]["id"] == "ntwEuuLyrVpH":
                    client = Calendly(settings.env("CALENDLY_TOKEN"))
                    invitee = client.get_resource(answer["url"])
                    event = client.get_resource(invitee["resource"]["event"])

                    speaker.name = " ".join(invitee["resource"]["name"].split())
                    speaker.email = invitee["resource"]["email"]

                    project.session = DateTimeTZRange(
                        event["resource"]["start_time"],
                        event["resource"]["end_time"],
                    )

        if speaker and project.session:
            speaker.save()
            project.speaker = speaker
            project.script = (
                Script.objects.filter(project__isnull=True)
                .exclude(recprompts__recording__gt="")
                .first()
            )
            project.save()

        return Response({}, status=200)


class CalendlyWebhookView(generics.CreateAPIView):
    permission_classes = [CalendlyPermission]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        event = request.data["event"]
        payload = request.data["payload"]

        if event in ("invitee.canceled", "invitee_no_show.created"):
            try:
                project = Project.objects.get(
                    session=DateTimeTZRange(
                        payload["scheduled_event"]["start_time"],
                        payload["scheduled_event"]["end_time"],
                    )
                )
            except Project.DoesNotExist:
                return Response({}, status=200)

            if payload["rescheduled"]:
                client = Calendly(settings.env("CALENDLY_TOKEN"))
                invitee = client.get_resource(payload["new_invitee"])
                event = client.get_resource(invitee["resource"]["event"])

                project.session = DateTimeTZRange(
                    event["resource"]["start_time"], event["resource"]["end_time"]
                )
                project.save()

            elif event == "invitee.canceled":
                if not project.script.recprompts.filter(recording__isnull=False):
                    project.delete()
                    project.speaker.delete()

            elif event == "invitee_no_show.created":
                if project.script:
                    if not project.script.recprompts.filter(recording__isnull=False):
                        project.no_show = True
                        project.script = None
                    else:
                        raise Exception(
                            "Can't mark a project as no_show if there are recordings"
                        )
                else:
                    project.no_show = True
                project.save()

        return Response({}, status=200)


class RecPromptView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = RecPrompt.objects.all()
    serializer_class = RecordingSerializer
    parser_classes = (MultiPartParser,)
    search_fields = ["mediaitem"]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get("script"):
            try:
                qs = qs.filter(script=self.request.query_params.get("script"))
            except:
                raise Http404
        return qs
