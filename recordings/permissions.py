from rest_framework.permissions import BasePermission
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
        try:
            SIGNING_KEY = settings.env("CALENDLY_WEBHOOK_SIGNING_KEY")

            signature = request.headers.get("Calendly-Webhook-Signature")

            values = [val for val in signature.split(",")]
            t, sig = [val.split("=")[1] for val in values]

            body = request.body.decode("utf-8")
            payload = f"{t}.{body}".encode("utf-8")
            mac = hmac.new(SIGNING_KEY.encode("utf-8"), payload, hashlib.sha256)

            if mac.hexdigest() == sig:
                tolerance = datetime.utcnow() - timedelta(minutes=3)

                if datetime.fromtimestamp(int(t)) > tolerance:
                    return True

            return False
        except:
            return False
