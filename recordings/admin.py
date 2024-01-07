from django.contrib import admin
from .models import Booking, Speaker

admin.site.register(Speaker)


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
