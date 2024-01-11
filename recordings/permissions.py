from rest_framework.permissions import BasePermission
from speech_recording import settings
import hashlib
import hmac
import base64


class CreateBookingPermission(BasePermission):
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
