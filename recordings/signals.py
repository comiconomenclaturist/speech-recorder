from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from speech_recording import settings
from calendly.client import Calendly
from .models import Project


@receiver(post_save, sender=Project)
def sync_to_calendly(sender, instance, **kwargs):
    """
    Set the calendly invitee to no show
    """
    if instance.no_show:
        client = Calendly(settings.env("CALENDLY_TOKEN"))

        events = client.request(
            "get",
            "scheduled_events",
            params={
                "user": client.user,
                "organization": client.organization,
                "min_start_time": instance.session.lower,
                "max_start_time": instance.session.lower,
            },
        )

        if len(events["collection"]) == 1:
            invitees = client.get_resource(f"{events['collection'][0]['uri']}/invitees")

            if not invitees["collection"][0]["no_show"]:
                payload = {"invitee": invitees["collection"][0]["uri"]}
                no_show = client.request("post", "invitee_no_shows", data=payload)
