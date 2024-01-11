from django.contrib import admin
from .models import *


class RecordingInline(admin.TabularInline):
    model = Recording


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    inlines = (RecordingInline,)


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


admin.site.register(Speaker)
admin.site.register(Recording)
