from argparse import Namespace

from django.utils import timezone
from lexmapr.pipeline import run

from config import celery_app
from lexmapr_django.pipeline.models import PipelineJob
from config.settings.base import CONFIG_DIR


@celery_app.task()
def run_lexmapr(job_id):
    """Execute ``PipelineJob`` object.

    This means running the original LexMapr pipeline using parameters
    set by the object, and in this function.

    If the execution succeeds, the object's ``complete`` field is set
    to ``True``.

    :param str job_id: ``id`` value of ``PipelineJob`` object
    """
    job = PipelineJob.objects.get(id=job_id)

    try:
        run(Namespace(input_file=job.input_file.path,
                      config=CONFIG_DIR, full=None,
                      output=job.output_file.path, version=False, bucket=False,
                      no_cache=True, profile="ifsac"))
    except Exception as e:
        job.err = True
        job.err_msg = str(e)

    job.complete = True
    job.save()


@celery_app.task()
def remove_stale_jobs():
    """Remove ``PipelineJob`` objects that have expired.

    This task is meant to be run periodically.
    """
    stale_jobs = PipelineJob.objects.filter(expires__lte=timezone.now())
    stale_jobs.delete()
