from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.postgres.forms.ranges import RangeWidget
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import Project, Speaker


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "session": RangeWidget(
                base_widget=forms.DateTimeInput(
                    attrs={"placeholder": "YYYY-MM-DD HH:MM"}
                )
            )
        }

    def clean(self):
        cleaned_data = super().clean()
        script = cleaned_data.get("script")
        changed_data = self.changed_data

        if changed_data:
            if not (len(changed_data) == 1 and changed_data[0] == "release_form"):
                if script and script.recprompts.filter(recording__gt=""):
                    msg = "Can't change a project if there are recordings"
                    self.add_error(self.changed_data[0], msg)

        return cleaned_data


class ArchiveForm(forms.Form):
    start = forms.DateField(widget=AdminDateWidget)
    end = forms.DateField(widget=AdminDateWidget)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("start") >= cleaned_data.get("end"):
            self.add_error("start", "Start date must be less than end date")


class SpeakerForm(forms.ModelForm):
    class Meta:
        model = Speaker
        fields = ("dateOfBirth", "name", "email", "sex", "accent")
        widgets = {
            "dateOfBirth": forms.widgets.DateInput(
                attrs={
                    "placeholder": "DD/MM/YYYY",
                    "class": "form-control",
                    "type": "date",
                    "max": (datetime.now().date() - relativedelta(years=18)),
                    "style": "text-transform: uppercase;",
                }
            ),
            "name": forms.widgets.TextInput(attrs={"class": "form-control"}),
            "email": forms.widgets.EmailInput(attrs={"class": "form-control"}),
            "sex": forms.widgets.Select(attrs={"class": "form-control"}),
            "accent": forms.widgets.Select(attrs={"class": "form-control"}),
        }
        labels = {"sex": "Gender"}


class BookingForm(forms.Form):
    slot = forms.DateTimeField(
        widget=forms.widgets.SplitDateTimeWidget(
            date_attrs={"label": "date", "type": "date"},
            time_attrs={"label": "time", "type": "time"},
        )
    )
    # class Meta:
    #     model = Project
    #     fields = ("session",)
    #     widgets = {
    #         "session": RangeWidget(
    #             forms.SplitDateTimeWidget(
    #                 date_attrs={"type": "date"},
    #                 time_attrs={"type": "time"},
    #             ),
    #         )
    #     }
