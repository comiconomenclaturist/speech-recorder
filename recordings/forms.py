from django import forms
from .models import Project
from django.contrib.admin.widgets import AdminDateWidget


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        script = cleaned_data.get("script")
        changed_data = self.changed_data

        if changed_data:
            if not (len(changed_data) == 1 and changed_data[0] == "release_form"):
                if script.recprompts.filter(recording__gt=""):
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
