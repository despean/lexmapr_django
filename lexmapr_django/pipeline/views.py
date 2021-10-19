from datetime import datetime

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from lexmapr_django.pipeline.forms import PipelineForm
from lexmapr_django.pipeline.models import PipelineJob
from lexmapr_django.pipeline.utils import (create_pipeline_job, results_to_matrix)
import boto3
from config.settings.base import env, APPS_DIR

def render_pipeline_form(request):
    """Render pipeline input form.

    If the user just submitted something, also renders a hyperlink to
    the eventual results of an associated ``PipelineJob`` object.
    """
    job_submission_status = None
    job = None
    err_msg = None

    # User just submitted something
    if "job_submission" in request.session:
        job_submission_status = request.session["job_submission"]["status"]

        # Succeeded in creating a ``PipelineJob`` object
        if job_submission_status == 200:
            job_id = request.session["job_submission"]["id"]
            job = PipelineJob.objects.get(id=job_id)
        else:
            err_msg = request.session["job_submission"]["msg"]

        request.session.pop("job_submission", None)
        request.session.modified = True

    return render(request, "pages/pipeline.html", {
        "form": PipelineForm(),
        "job_submission_status": job_submission_status,
        "job": job,
        "err_msg": err_msg
    })


@require_POST
def process_pipeline_input(request):
    """``PipelineJob`` object created from ``PipelineForm`` submission.

    Job information is also stored in session, for purposes described
    in ``render_pipeline_form``.
    """
    form = PipelineForm(request.POST, request.FILES)
    request.session["job_submission"] = {}

    if form.is_valid():
        input_file = form.cleaned_data["input_file"]
        job_id = create_pipeline_job(input_file)

        request.session["job_submission"] = {"status": 200, "id": job_id,
                                             "msg": None}
    else:
        request.session["job_submission"] = {"status": 400, "id": None,
                                             "msg": form.errors}

    return redirect("pipeline:")


def render_pipeline_results(request, job_id):
    """Renders ``PipelineJob`` object ``output_file`` contents.

    If ``PipelineJob.complete`` is ``False``, the user is notified that
    their job is still running.

    :param str job_id: ``id`` value of ``PipelineJob`` object
    """
    job = get_object_or_404(PipelineJob, id=job_id,
                            expires__gte=datetime.now())
    url = ""
    results_matrix = results_to_matrix(job_id)
    if job.complete:
        try:
            session = boto3.Session(
                aws_access_key_id=env("DJANGO_AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=env("DJANGO_AWS_SECRET_ACCESS_KEY"),
                region_name=env("DJANGO_AWS_S3_REGION_NAME")
            )
            s3_client = session.client('s3')
            filename = str(job_id)+".tsv"
            res = s3_client.upload_file(str(APPS_DIR)+'/media/output_files/'+filename, 'lexmaprmediafiles', filename)
            url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': 'lexmaprmediafiles', 'Key': filename},
                ExpiresIn=86400)
            print("url:", url)
        except Exception as e:
            print(e)
    return render(request, "pages/pipeline_results.html", {
        "job": job, "results_matrix": results_matrix, "url": url
    })
