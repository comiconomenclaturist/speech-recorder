from rest_framework import generics
from rest_framework import permissions
from django.views.decorators.csrf import csrf_exempt
from psycopg2.extras import DateTimeTZRange
from speech_recording import settings
from speech_recorder.models import Project, Speaker
import hashlib
import hmac
import base64
import json
import requests


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
    r = requests.get(
        url, headers={"Authorization": f"Bearer {settings.env('CALENDLY_TOKEN')}"}
    )
    if r.status_code == 200:
        return json.loads(r.text)
    raise Exception(r)


class CreateBookingView(generics.CreateAPIView):
    permission_classes = [CreateBookingPermission]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        data = request.data
        project = Project()
        speaker = Speaker()

        if data["event_type"] == "form_response":
            for answer in data["form_response"]["answers"]:
                if answer["field"]["id"] == "LwvCDF97Z3oh":
                    speaker.sex = answer["choice"]["label"]
                elif answer["field"]["id"] == "BFHvuavpm2QD":
                    speaker.dob = answer["date"]
                elif answer["field"]["id"] == "R3boiK7GwVaq":
                    speaker.accent = answer["choice"]["label"]
                elif answer["field"]["id"] == "ntwEuuLyrVpH":
                    invitee = calendly(answer["url"])
                    speaker.forename = invitee["resource"]["first_name"]
                    speaker.name = invitee["resource"]["last_name"]

                    event = calendly(invitee["resource"]["event"])
                    project.session = DateTimeTZRange(
                        event["resource"]["start_time"],
                        event["resource"]["end_time"],
                    )
            project.save()
            speaker.save()
        return
