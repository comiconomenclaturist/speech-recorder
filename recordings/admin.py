from django.contrib import admin
from dateutil.relativedelta import relativedelta
from urllib.parse import urlparse
from .models import *
from .filters import *
import datetime


@admin.register(RecPrompt)
class RecPromptAdmin(admin.ModelAdmin):
    model = RecPrompt
    list_display = ("__str__", "script", "project")
    list_filter = (ProjectFilter,)
    search_fields = ("mediaitem",)

    def project(self, obj):
        if obj.script and obj.script.project:
            return obj.script.project

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.select_related("script__project")


class RecPromptInline(admin.TabularInline):
    model = RecPrompt


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    inlines = (RecPromptInline,)
    list_display = ("__str__", "project")
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


def current():
    this_month = datetime.datetime.today().replace(day=1)
    return this_month.combine(this_month, datetime.time())


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    model = Project

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.select_related("speaker", "script").only(
            "session", "speaker__name", "script"
        )

    def booking(self, obj):
        if obj:
            return obj.session.lower

    booking.admin_order_field = "session__startswith"

    list_display = ("booking", "speaker", "script", "no_show")
    list_filter = (
        UpcomingFilter,
        (
            "session",
            DateTimeTZRangeFilterBuilder(
                title="Session",
                default_start=current(),
                default_end=current() + relativedelta(months=1),
            ),
        ),
        "no_show",
    )
    search_fields = ("speaker__name", "speaker__email")
    raw_id_fields = ("script", "speaker")


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
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
