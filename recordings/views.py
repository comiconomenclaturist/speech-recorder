from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from psycopg2.extras import DateTimeTZRange
from urllib.parse import urlparse
from speech_recording import settings

# from speech_recording.xml_renderer import CustomXMLRenderer
from .models import Booking, Speaker
from .serializers import SpeakerSerializer
import hashlib
import hmac
import base64
import json
import requests


# class SpeakerXMLRenderer(CustomXMLRenderer):
#     root_tag_name = "speakers"
#     item_tag_name = "speakers"


class SpeakersViewset(ModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    # renderer_classes = [SpeakerXMLRenderer]


class CreateBookingPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        signature = request.headers.get("typeform-signature")

        if not signature:
            return False

        sha_name, signature = signature.split("=", 1)

        if sha_name != "sha256":
            return False

        SECRET = settings.env("TYPEFORM_SECRET_KEY")
        digest = hmac.new(SECRET.encode("utf-8"), request.body, hashlib.sha256).digest()
        e = base64.b64encode(digest).decode()

        return e == signature


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


class CreateBookingView(generics.CreateAPIView):
    permission_classes = [CreateBookingPermission]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        data = request.data
        booking = Booking()
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
                    booking.session = DateTimeTZRange(
                        event["resource"]["start_time"],
                        event["resource"]["end_time"],
                    )

            speaker.save()
            booking.speaker = speaker
            booking.save()

        return Response({}, status=200)
