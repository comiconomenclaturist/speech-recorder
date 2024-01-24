from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now


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
