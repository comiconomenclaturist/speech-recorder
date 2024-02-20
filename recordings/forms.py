from django import forms
from django.forms import widgets
from .models import RecPrompt


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
