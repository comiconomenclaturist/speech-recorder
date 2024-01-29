from requests import request
import json


class Calendly:
    def __init__(self, token):
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def request(self, method, path, data={}, params=None):
        url = f"{self.base_url}/{path}"
        if data:
            r = request(method, url, json=data, headers=self.headers)
        else:
            r = request(method, url, headers=self.headers, params=params)

        if "application/json" in r.headers["Content-Type"] and r.status_code == 200:
            return json.loads(r.text)

        raise Exception(r.text)

    def get_user(self):
        response = self.request("GET", "users/me")
        self.organization = response["resource"]["current_organization"]
        self.user = response["resource"]["uri"]

    def list_webhooks(self):
        if not hasattr(self, "organization") or not hasattr(self, "user"):
            self.get_user()

        querystring = {
            "scope": "user",
            "organization": self.organization,
            "user": self.user,
        }
        return self.request("GET", "webhook_subscriptions", params=querystring)

    def create_webhook(self, callback, signing_key):
        if not hasattr(self, "organization") or not hasattr(self, "user"):
            self.get_user()

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
