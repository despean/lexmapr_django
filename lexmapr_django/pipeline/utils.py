from os.path import splitext
from random import getrandbits

from django.core.files.base import ContentFile
from django.db import transaction

from lexmapr_django.pipeline.models import PipelineJob
from lexmapr_django.pipeline.tasks import run_lexmapr


def create_pipeline_job(input_file):
    """Create ``PipelineJob`` object.

    :param input_file: Input file uploaded by user in ``PipelineForm``
        instance
    :type input_file:
        django.core.files.uploadedfile.InMemoryUploadedFile
    :returns: Created ``PipelineJob`` object ``id`` value
    :rtype: str
    """
    job_id = getrandbits(128)
    job = PipelineJob(id=job_id)
    job.save()

    _, ext = splitext(input_file.name)
    job.input_file.save(str(job_id) + ext, input_file)
    job.output_file.save(str(job_id) + ".tsv", ContentFile("".encode("utf-8")))

    # Wait for above transactions to complete before calling task
    transaction.on_commit(lambda: run_lexmapr.delay(job_id))

    return job_id


def results_to_matrix(job_id):
    """Convert ``output_file`` contents of job to matrix.

    The matrix is tab-delimited.

    :param str job_id: ``id`` value of ``PipelineJob`` object
    :returns: Tab-delimited matrix
    :rtype: list of list
    """
    job = PipelineJob.objects.get(id=job_id)
    table = []

    results = job.output_file.read().decode("utf-8")
    results_rows = results.split("\n")
    for results_row in results_rows:
        table.append(results_row.split("\t"))

    # Remove row corresponding to empty row at end of results
    table.pop()

    return table
