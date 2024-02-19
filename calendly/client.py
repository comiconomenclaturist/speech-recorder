from requests import request
from urllib.parse import urlparse
import json


class Calendly:
    def __init__(self, token):
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.get_user()

    def request(self, method, path, data={}, params=None):
        path = urlparse(path).path
        url = f"{self.base_url}/{path}"

        if data:
            r = request(method, url, json=data, headers=self.headers)
        else:
            r = request(method, url, headers=self.headers, params=params)

        if r.status_code in (200, 201):
            if "application/json" in r.headers.get("Content-Type"):
                return json.loads(r.text)
            return r.text

        raise Exception(r.text)

    def get_user(self):
        response = self.request("GET", "users/me")
        self.organization = response["resource"]["current_organization"]
        self.user = response["resource"]["uri"]

    def get_resource(self, url):
        return self.request("GET", url)

    def list_webhooks(self):
        querystring = {
            "scope": "user",
            "organization": self.organization,
            "user": self.user,
        }
        return self.request("GET", "webhook_subscriptions", params=querystring)

    def create_webhook(self, callback, signing_key):
        payload = {
            "url": callback,
            "events": [
                "invitee.created",
                "invitee.canceled",
                "invitee_no_show.created",
            ],
            "organization": self.organization,
            "user": self.user,
            "scope": "user",
            "signing_key": signing_key,
        }
        return self.request("POST", "webhook_subscriptions", data=payload)

    def delete_webhook(self, webhook):
        return self.request("DELETE", f"webhook_subscriptions/{webhook}")
