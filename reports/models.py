from django.db import models
from django.core.validators import FileExtensionValidator
from recordings.fields import CustomFileField
import os


class Description(models.Model):
    name = models.CharField(max_length=128)
    equipment = models.TextField(null=False)
    location = models.TextField(null=False)

    def __str__(self):
        return self.name


class Archive(models.Model):
    description = models.ForeignKey(Description, on_delete=models.PROTECT)
    file = CustomFileField(
        upload_to="archived", validators=[FileExtensionValidator(["zip"])], null=False
    )

    def __str__(self):
        if self.file:
            return os.path.basename(self.file.name)
        return super().__str__()
