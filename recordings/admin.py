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


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    model = Project

    def start(self, obj):
        if obj:
            return obj.session.lower

    def end(self, obj):
        if obj:
            return obj.session.upper

    list_display = ("start", "end", "speaker")
    list_filter = (UpcomingFilter,)
    search_fields = ("speaker__name",)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    model = Speaker
    list_display = ("__str__", "email")


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
