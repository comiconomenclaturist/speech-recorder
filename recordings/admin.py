from django.contrib import admin
from dateutil.relativedelta import relativedelta
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse
from urllib.parse import urlparse
from zipfile import ZipFile
from .models import *
from .views import ProjectsViewSet, SpeakersViewSet, ScriptsViewSet
from .forms import RecPromptAdminForm, ProjectAdminForm
from .filters import *
from speech_recording import settings
import datetime
import io


class ArchiveMixin:
    def _check_project(self, obj, default):
        if obj:
            if obj.__class__ == RecPrompt and obj.recording:
                return False
            try:
                if obj.project.script.recprompts.filter(recording__gt="").exists():
                    return False
            except:
                pass
        return default

    def has_change_permission(self, request, obj=None):
        default = super().has_change_permission(request, obj)
        return self._check_project(obj, default)

    def has_delete_permission(self, request, obj=None):
        default = super().has_delete_permission(request, obj)
        return self._check_project(obj, default)


@admin.register(RecPrompt)
class RecPromptAdmin(ArchiveMixin, admin.ModelAdmin):
    model = RecPrompt
    list_display = ("__str__", "script", "project")
    list_filter = (ProjectFilter, RecordedFilter)
    search_fields = ("mediaitem",)
    readonly_fields = ("size",)

    def project(self, obj):
        if obj.script and obj.script.project:
            return obj.script.project

    def size(self, obj):
        return obj.size

    size.short_description = "Filesize"

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.select_related("script__project")


class RecPromptInline(admin.TabularInline):
    def size(self, obj):
        return obj.size

    size.short_description = "Filesize"

    model = RecPrompt
    form = RecPromptAdminForm
    readonly_fields = ("size",)


@admin.register(Script)
class ScriptAdmin(ArchiveMixin, admin.ModelAdmin):
    def recorded(self, obj=None):
        if obj and obj.recprompts.filter(recording__gt=""):
            return True
        return False

    recorded.boolean = True

    inlines = (RecPromptInline,)
    list_display = ("__str__", "project", "recorded")
    search_fields = ("project__speaker__name", "project__speaker__email")

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term
        )
        if search_term:
            queryset |= self.model.objects.filter(
                recprompts__mediaitem__contains=search_term
            )
            may_have_duplicates = True

        return queryset, may_have_duplicates

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        url = urlparse(request.META.get("HTTP_REFERER"))

        if request.GET.get("_popup") and url.path:
            if url.path.startswith("/admin/recordings/project/"):
                qs = qs.filter(project__isnull=True)

        return qs.select_related("project", "project__speaker").only(
            "project__session", "project__speaker__name"
        )


def current_month():
    this_month = datetime.datetime.today().replace(day=1)
    return this_month.combine(this_month, datetime.time())


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    model = Project
    form = ProjectAdminForm

    def download(self, *args, **kwargs):
        project = Project.objects.get(pk=kwargs.get("pk"))

        project_view = ProjectsViewSet.as_view({"get": "retrieve"})
        speaker_view = SpeakersViewSet.as_view({"get": "retrieve"})
        script_view = ScriptsViewSet.as_view({"get": "retrieve"})

        project_xml = project_view(*args, **kwargs).render()
        speaker_xml = speaker_view(*args, **{"pk": project.speaker.pk}).render()
        script_xml = script_view(*args, **{"pk": project.script.pk}).render()
        dtd_file = os.path.join(settings.STATIC_ROOT, "SpeechRecPrompts_4.dtd")

        buffer = io.BytesIO()

        with ZipFile(buffer, "w") as zf:
            zf.writestr(f"{project.name}_project.prj", project_xml.content)
            zf.writestr(f"{project.speaker.pk}_speakers.xml", speaker_xml.content)
            zf.writestr(f"{project.script.pk}_script.xml", script_xml.content)
            zf.write(dtd_file, arcname="SpeechRecPrompts_4.dtd")

        response = HttpResponse(buffer.getvalue())
        response["Content-Type"] = "application/x-zip-compressed"
        response["Content-Disposition"] = f"attachment; filename={project.name}.zip"
        return response

    def get_urls(self, *args, **kwargs):
        urls = super().get_urls(*args, **kwargs)
        return [
            path("download/<int:pk>/", self.download),
        ] + urls

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("speaker", "script").only(
            "session", "speaker__name", "script"
        )

    def project_zip(self, obj):
        if obj:
            return format_html(f'<a href="download/{obj.pk}/">Download</a>')

    def booking(self, obj):
        if obj:
            return obj.session.lower

    booking.admin_order_field = "session__startswith"

    fields = (
        "session",
        "speaker",
        "script",
        "RecordingConfiguration",
        "recordingMixerName",
        "playbackMixerName",
        "no_show",
        "release_form",
        "microphone",
        "soundcard",
        "archive",
    )
    raw_id_fields = ("script", "speaker")
    readonly_fields = ("archive",)
    search_fields = ("speaker__name", "speaker__email")
    list_display = ("booking", "speaker", "script", "project_zip", "no_show")
    list_filter = (
        UpcomingFilter,
        (
            "session",
            DateTimeTZRangeFilterBuilder(
                title="Session",
                default_start=current_month(),
                default_end=current_month() + relativedelta(months=1),
            ),
        ),
        "no_show",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.script and obj.script.recprompts.filter(recording__gt=""):
            return [f for f in self.fields if f != "release_form"]
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        if obj.no_show and obj.script:
            obj.script = None
        return super().save_model(request, obj, form, change)


@admin.register(Speaker)
class SpeakerAdmin(ArchiveMixin, admin.ModelAdmin):
    model = Speaker
    list_display = ("__str__", "sex", "email", "booking")
    list_filter = ("sex",)
    search_fields = ("name", "email")

    def booking(self, obj):
        if obj:
            return obj.project.session.lower

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("project").only("name", "sex", "email")


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
admin.site.register(Microphone)
admin.site.register(Soundcard)
