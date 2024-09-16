from django.contrib import admin
from .models import CalendlyForm


@admin.register(CalendlyForm)
class CalendlyFormAdmin(admin.ModelAdmin):
    model = CalendlyForm
    list_display = ("name", "language", "private")
