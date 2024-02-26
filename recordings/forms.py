from django import forms
from django.forms import widgets
from .models import Project, RecPrompt


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
                if script.recprompts.filter(recording__isnull=False):
                    msg = "Can't change a project if there are recordings"
                    self.add_error(self.changed_data[0], msg)

        return cleaned_data


class RecordingWidget(widgets.ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        if value:
            html += f'<p><audio controls src="{value.url}"></audio></p>'
        return html


class RecPromptAdminForm(forms.ModelForm):
    class Meta:
        model = RecPrompt
        fields = "__all__"
        widgets = {
            "recording": RecordingWidget(),
        }
