from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilter
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.db.models import Q
from psycopg2.extras import DateTimeTZRange


class ProjectFilter(admin.SimpleListFilter):
    title = _("Assigned")
    parameter_name = "assigned"

    def lookups(self, request, model_admin):
        return [
            ("true", _("Yes")),
            ("false", _("No")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.filter(script__project__isnull=False)
        if self.value() == "false":
            return queryset.filter(script__project__isnull=True)


class UpcomingFilter(admin.SimpleListFilter):
    title = _("Upcoming")
    parameter_name = "upcoming"

    def lookups(self, request, model_admin):
        return [
            ("true", _("Yes")),
            ("false", _("No")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.filter(session__startswith__gte=now())
        if self.value() == "false":
            return queryset.filter(session__startswith__lte=now())


class DateTimeTZRangeFilter(DateTimeRangeFilter):
    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)

        if date_value_gte:
            start = self.make_dt_aware(date_value_gte, self.get_timezone(request))
            query_params[f"{self.field_path}__startswith__gte"] = start

        if date_value_lte:
            end = self.make_dt_aware(date_value_lte, self.get_timezone(request))
            query_params[f"{self.field_path}__startswith__lte"] = end

        if date_value_gte and date_value_lte:
            query_params[f"{self.field_path}__overlap"] = DateTimeTZRange(start, end)

        return query_params


def DateTimeTZRangeFilterBuilder(title=None, default_start=None, default_end=None):
    filter_cls = type(
        str("DateTimeRangeFilter"),
        (DateTimeTZRangeFilter,),
        {
            "__from_builder": True,
            "default_title": title,
            "default_start": default_start,
            "default_end": default_end,
        },
    )

    return filter_cls


class RecordedFilter(admin.SimpleListFilter):
    title = _("Recorded")
    parameter_name = "recorded"

    def lookups(self, request, model_admin):
        return [
            ("true", _("Yes")),
            ("false", _("No")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.filter(recording__gt="")
        if self.value() == "false":
            return queryset.filter(Q(recording__isnull=True) | Q(recording=""))
