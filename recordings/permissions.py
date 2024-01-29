from rest_framework.permissions import BasePermission
from django.utils.timezone import now
from datetime import datetime, timedelta
from speech_recording import settings
import hashlib
import hmac
import base64


class TypeFormPermission(BasePermission):
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


class CalendlyPermission(BasePermission):
    def has_permission(self, request, view):
        SIGNING_KEY = settings.env("CALENDLY_WEBHOOK_SIGNING_KEY")

        try:
            signature = request.headers.get("Calendly-Webhook-Signature")

            values = [val for val in signature.split(",")]
            t, sig = [val.split("=")[1] for val in values]

            payload = f"{t}.{request.body}"
            digest = hmac.new(
                SIGNING_KEY.encode("utf-8"), payload, hashlib.sha256
            ).digest()

            e = base64.b64encode(digest).decode()

            if e == sig:
                if datetime.fromtimestamp(t) > now() - timedelta(minutes=3):
                    return True
        except Exception as e:
            with open("/tmp/test.txt", "a") as f:
                f.write("\n")
                f.write(e)
                f.write("*" * 40)
                f.write("\n")
            return False

        return False
