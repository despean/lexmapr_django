from datetime import datetime

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from lexmapr_django.pipeline.forms import PipelineForm
from lexmapr_django.pipeline.models import PipelineJob
from lexmapr_django.pipeline.utils import (create_pipeline_job, results_to_matrix)


def render_pipeline_form(request):
    """Render pipeline input form.

    If the user just submitted a form, also renders a hyperlink to the
    eventual results of their job.
    """
    job_submission_status = None
    job = None

    # Just tried to create a job through ``process_pipeline_input``
    if "job_submission" in request.session:
        job_submission_status = request.session["job_submission"]["status"]

        # Succeeded in creating a job
        if job_submission_status == 200:
            job_id = request.session["job_submission"]["id"]
            job = PipelineJob.objects.get(id=job_id)

        request.session.pop("job_submission", None)
        request.session.modified = True

    return render(request, "pages/pipeline.html", {
        "form": PipelineForm(),
        "job_submission_status": job_submission_status,
        "job": job
    })


@require_POST
def process_pipeline_input(request):
    """Submits data from pipeline form submission to pipeline job.

    Also stores job information in session.
    """
    form = PipelineForm(request.POST, request.FILES)
    request.session["job_submission"] = {}

    if form.is_valid():
        input_file = form.cleaned_data["input_file"]
        job_id = create_pipeline_job(input_file)

        request.session["job_submission"] = {"status": 200, "id": job_id}
    else:
        request.session["job_submission"] = {"status": 400, "id": None}

    return redirect("pipeline:")


def render_pipeline_results(request, job_id):
    """TODO:..."""
    job = get_object_or_404(PipelineJob, id=job_id,
                            expires__gte=datetime.now())

    # Live, up-to-date results in matrix-form
    results_matrix = results_to_matrix(job)

    return render(request, "pages/pipeline_results.html", {
        "job": job, "results_matrix": results_matrix
    })
