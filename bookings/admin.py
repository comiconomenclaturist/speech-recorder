from django.contrib import admin
from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    model = Booking

    def start(self, obj):
        if obj:
            return obj.session.lower

    def end(self, obj):
        if obj:
            return obj.session.upper

    list_display = ("start", "end", "speaker")
