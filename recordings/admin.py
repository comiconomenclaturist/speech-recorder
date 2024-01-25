from django.contrib import admin
from .models import *
from .filters import *


@admin.register(RecPrompt)
class RecPromptAdmin(admin.ModelAdmin):
    model = RecPrompt
    list_display = ("__str__", "script", "project")
    list_filter = (ProjectFilter,)

    def project(self, obj):
        if obj.script and obj.script.project:
            return obj.script.project


class RecPromptInline(admin.TabularInline):
    model = RecPrompt


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    inlines = (RecPromptInline,)
    list_display = ("__str__", "project")
    search_fields = ("project__speaker__name", "project__speaker__email")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    model = Project

    def booking(self, obj):
        if obj:
            return obj.session.lower

    booking.admin_order_field = "session__startswith"

    list_display = ("booking", "speaker", "script")
    list_filter = (UpcomingFilter,)
    search_fields = ("speaker__name", "speaker__email")


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    model = Speaker
    list_display = ("__str__", "sex", "email", "booking")
    list_filter = ("sex",)
    search_fields = ("name", "email")

    def booking(self, obj):
        if obj:
            return obj.project.session.lower


class MixerNameAdmin(admin.ModelAdmin):
    list_display = ("name", "default")
    list_editable = ("default",)


@admin.register(RecordingMixerName)
class RecordingMixerNameAdmin(MixerNameAdmin):
    pass


@admin.register(PlaybackMixerName)
class PlaybackMixerNameAdmin(MixerNameAdmin):
    pass


admin.site.register(RecordingConfig)
admin.site.register(Format)
