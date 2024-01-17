from django.contrib import admin
from .models import *


class RecordingInline(admin.TabularInline):
    model = Recording


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    inlines = (RecordingInline,)
    list_display = ("__str__", "speaker")


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


admin.site.register(Recording)
admin.site.register(RecordingConfig)
admin.site.register(Format)
