from django.urls import path, re_path
from lexmapr_django.pipeline.api import *

from lexmapr_django.pipeline.views import (
    render_pipeline_form,
    process_pipeline_input,
    render_pipeline_results
)

app_name = "pipeline"
urlpatterns = [
    path("", view=render_pipeline_form, name=""),
    path("api/upload", view=FileUpload.as_view(), name="file_upload"),
    path("submit", view=process_pipeline_input, name="submit"),
    re_path("^temp/(?P<job_id>\w+)/$", view=render_pipeline_results,
            name="temp"),
    re_path("^api/temp/(?P<job_id>\w+)/$", view=FileUploadResult.as_view(),
            name="file_upload_res")
]
