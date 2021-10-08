from datetime import timedelta
import os

from django.db.models import (
    Model, BooleanField, CharField, DateTimeField, FileField, TextField
)
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone


def get_expiry_date():
    return timezone.now() + timedelta(days=7)


class PipelineJob(Model):
    """Represents job to be run on the original LexMapr pipeline."""
    id = CharField(max_length=128, primary_key=True)
    complete = BooleanField(default=False)
    input_file = FileField(upload_to="input_files/", blank=True)
    output_file = FileField(upload_to="output_files/", blank=True)
    expires = DateTimeField(default=get_expiry_date)
    err = BooleanField(default=False)
    err_msg = TextField(blank=True)

    def get_absolute_url(self):
        return reverse('pipeline:temp', kwargs={"job_id": self.id})

    def get_api_absolute_url(self):
        return reverse('pipeline:file_upload_res', kwargs={"job_id": self.id})



@receiver(post_delete, sender=PipelineJob)
def auto_delete_files(sender, instance, **kwargs):
    """Delete PipelineJob input, output files when model is deleted."""
    if instance.input_file:
        if os.path.isfile(instance.input_file.path):
            os.remove(instance.input_file.path)

    if instance.output_file:
        if os.path.isfile(instance.output_file.path):
            os.remove(instance.output_file.path)
