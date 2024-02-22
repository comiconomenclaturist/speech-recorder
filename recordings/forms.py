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

        if cleaned_data.get("no_show") and script:
            if script.recprompts.filter(recording__isnull=False):
                msg = "Can't mark a project as 'No show' if there are recordings"
                self.add_error("no_show", msg)

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
