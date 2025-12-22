from django.contrib import admin
from dateutil.relativedelta import relativedelta
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from urllib.parse import urlparse
from zipfile import ZipFile
from .models import *
from .views import ProjectsViewSet, SpeakersViewSet, ScriptsViewSet
from .forms import ProjectAdminForm
from .filters import *
from speech_recording import settings
from celery import current_app
from .forms import ArchiveForm
import datetime
import csv
import io


class ProjectPermissionMixin:
    def _check_recordings(self, obj, default):
        q = Q(recording__gt="")

        if obj:
            if obj.__class__ == RecPrompt and obj.recording:
                return False
            elif obj.__class__ == Project and obj.script:
                if obj.script.recprompts.filter(q).exists():
                    return False
            elif obj.__class__ in (Speaker, Script) and hasattr(obj, "project"):
                if obj.project.script:
                    if obj.project.script.recprompts.filter(q).exists():
                        return False
        return default

    def has_delete_permission(self, request, obj=None):
        default = super().has_delete_permission(request, obj)
        return self._check_recordings(obj, default)


class OtherPermissionMixin(ProjectPermissionMixin):
    def has_change_permission(self, request, obj=None):
        default = super().has_change_permission(request, obj)
        return self._check_recordings(obj, default)


class RecordingMixin:
    def _filesize(self, obj):
        return obj._filesize

    _filesize.short_description = "Filesize"

    def _recording(self, obj):
        return obj._recording

    _recording.short_description = "Recording"


@admin.register(RecPrompt)
class RecPromptAdmin(OtherPermissionMixin, RecordingMixin, admin.ModelAdmin):
    model = RecPrompt
    list_display = ("__str__", "script", "project")
    list_filter = (ProjectFilter, RecordedFilter)
    search_fields = ("mediaitem",)
    readonly_fields = ("_recording", "filesize")
    exclude = ("recording",)

    def project(self, obj):
        if obj.script and obj.script.project:
            return obj.script.project

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.select_related("script__project")


class RecPromptInline(RecordingMixin, admin.TabularInline):
    model = RecPrompt
    readonly_fields = ("_recording", "_filesize")
    exclude = ("recording",)


@admin.register(Script)
class ScriptAdmin(OtherPermissionMixin, admin.ModelAdmin):
    def recorded(self, obj=None):
        if obj and obj.recprompts.filter(recording__gt=""):
            return True
        return False

    recorded.boolean = True

    inlines = (RecPromptInline,)
    list_display = ("__str__", "project", "recorded")
    search_fields = ("project__speaker__name", "project__speaker__email")
    list_filter = (StatusFilter, LanguageFilter)

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
class ProjectAdmin(ProjectPermissionMixin, admin.ModelAdmin):
    model = Project
    form = ProjectAdminForm
    change_list_template = "admin/recordings/project/change_list.html"

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

    def archive(self, request, *args, **kwargs):
        context = {
            "opts": self.model._meta,
            "site_title": "Speech Recorder admin",
            "title": "Projects",
            "subtitle": "Create archive",
            "form": ArchiveForm(),
        }

        if request.method == "POST":
            form = ArchiveForm(data=request.POST)

            if form.is_valid():
                start = form.cleaned_data.get("start")
                end = form.cleaned_data.get("end")
                language = form.cleaned_data.get("language")

                i = current_app.control.inspect()

                for worker, tasks in i.active().items():
                    for task in tasks:
                        if task["name"] == "Create archive":
                            self.message_user(
                                request,
                                "Create archive task is already running",
                                level="ERROR",
                            )
                            return render(
                                request,
                                "admin/recordings/project/archive.html",
                                context=context,
                            )

                current_app.send_task("Create archive", (start, end, language))
                self.message_user(
                    request, f"Creating an archive of projects from {start} to {end}..."
                )
                return HttpResponseRedirect(
                    reverse("admin:recordings_project_changelist")
                )
            else:
                context["form"] = form

        return render(request, "admin/recordings/project/archive.html", context=context)

    def get_urls(self, *args, **kwargs):
        urls = super().get_urls(*args, **kwargs)
        return [
            path("download/<int:pk>/", self.download),
            path("archive/", self.archive),
        ] + urls

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("speaker", "script").only(
            "session", "speaker__name", "script"
        )

    def project_zip(self, obj):
        if obj and obj.script:
            return format_html(f'<a href="download/{obj.pk}/">Download</a>')

    def booking(self, obj):
        if obj:
            return obj.session.lower

    booking.admin_order_field = "session__startswith"

    fields = (
        "session",
        "private",
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
    list_display = ("booking", "speaker", "script", "project_zip", "no_show", "private")
    ordering = ("-session__startswith",)
    list_filter = (
        UpcomingFilter,
        "private",
        ProjectRecordedFilter,
        ("release_form", admin.EmptyFieldListFilter),
        (
            "session",
            DateTimeTZRangeFilterBuilder(
                title="Session",
                default_start=current_month(),
                default_end=current_month() + relativedelta(months=1),
            ),
        ),
        "no_show",
        "archive",
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
class SpeakerAdmin(OtherPermissionMixin, admin.ModelAdmin):
    def booking(self, obj):
        if obj:
            return obj.project.session.lower

    booking.admin_order_field = "project__session__startswith"

    def no_show(self, obj):
        if obj and obj.project:
            return obj.project.no_show

    no_show.boolean = True

    def recorded(self, obj):
        if obj:
            return obj.recorded

    recorded.boolean = True

    model = Speaker
    list_display = (
        "__str__",
        "sex",
        "email",
        "accent",
        "booking",
        "no_show",
        "recorded",
    )
    list_filter = (
        "sex",
        "project__no_show",
        AccentFilter,
        SpeakerRecordedFilter,
        (
            "project__session",
            DateTimeTZRangeFilterBuilder(
                title="Session",
                default_start=current_month(),
                default_end=current_month() + relativedelta(months=1),
            ),
        ),
    )
    search_fields = ("name", "email")
    actions = ("export_to_CSV",)

    @admin.action
    def export_to_CSV(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f"attachment; filename=Speech Recording {self.model._meta.model_name}.csv"
        )
        writer = csv.writer(response)
        writer.writerow(["name", "email", "booking", "no_show", "recorded"])

        for obj in queryset:
            writer.writerow(
                [
                    obj.name,
                    obj.email,
                    obj.project.session.lower,
                    obj.project.no_show,
                    obj.recorded,
                ]
            )

        return response

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


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    list_display = ("sampleRate", "sampleSizeInBits", "channels")


@admin.register(RecordingConfig)
class RecordingConfigAdmin(admin.ModelAdmin):
    list_display = ("url", "captureScope", "Format", "default")


admin.site.register(Microphone)
admin.site.register(Soundcard)
