from django.apps import AppConfig


class SpeechRecorderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recordings"

    def ready(self):
        import recordings.signals
