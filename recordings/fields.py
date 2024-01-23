from django.db import models


class RecordingField(models.FileField):
    """
    Delete the file from storage if the model field is cleared
    """

    def save_form_data(self, instance, data):
        if data is not None:
            file = getattr(instance, self.attname)
            if file != data:
                file.delete(save=False)
        super(RecordingField, self).save_form_data(instance, data)
