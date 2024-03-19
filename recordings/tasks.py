from celery import shared_task
from speech_recording import settings
from calendly.client import Calendly
from django.utils.timezone import now
from recordings.models import Project
from psycopg2.extras import DateTimeTZRange


@shared_task(name="Check missing bookings")
def check_missing_bookings():
    client = Calendly(settings.env("CALENDLY_TOKEN"))

    querystring = {
        "min_start_time": now().strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
        "organization": client.organization,
    }

    bookings = client.request("get", "scheduled_events", params=querystring)
    missing = []

    while bookings.get("collection"):
        for booking in bookings["collection"]:
            if not booking.get("cancellation"):
                try:
                    Project.objects.get(
                        session=DateTimeTZRange(
                            booking["start_time"], booking["end_time"]
                        )
                    )
                except Project.DoesNotExist:
                    invitees = client.request("get", f"{booking['uri']}/invitees")
                    missing.append(
                        {
                            "booking": booking["start_time"],
                            "name": invitees["collection"][0]["name"],
                            "email": invitees["collection"][0]["email"],
                        }
                    )
        if bookings["pagination"]["next_page_token"]:
            querystring.update(
                {"page_token": bookings["pagination"]["next_page_token"]}
            )
            bookings = client.request("get", "scheduled_events", params=querystring)
        else:
            break

    return missing
