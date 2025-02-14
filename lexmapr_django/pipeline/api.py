# Recieve file input from api to create job pipeline
from pprint import pprint
from django.shortcuts import get_object_or_404
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from django.core import serializers

from lexmapr_django.pipeline.models import PipelineJob
from lexmapr_django.pipeline.serializers import PipelineJobSerializer
from lexmapr_django.pipeline.utils import create_pipeline_job
import json
import boto3
from config.settings.base import env, APPS_DIR


class FileUpload(APIView):

    def get(self, request, job_id, *args):
        return Response({'status': 400, 'error': 'Only POST method supported.'})

    def post(self, request, *args):
        res = {}
        if "inputFile" in request.data:
            job_id = create_pipeline_job(request.data['inputFile'])
            job = PipelineJob.objects.get(id=job_id)
            res = {"status": 200, "id": job_id,
                   "output_url": job.get_api_absolute_url(),
                   "complete": job.complete
                   }
        else:
            res = {"status": 400, "id": None,
                   "msg": "No input file.[inputFile] required."}
        return Response(res)


class FileUploadResult(APIView):

    def get(self, request, job_id, *args):
        job = get_object_or_404(PipelineJob, id=job_id,
                                expires__gte=datetime.now())
        res = {}
        if job is not None:
            session = boto3.Session(
                aws_access_key_id=env("DJANGO_AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=env("DJANGO_AWS_SECRET_ACCESS_KEY")
            )
            s3_client = session.client('s3')
            filename = str(job_id) + ".tsv"
            result = s3_client.upload_file(str(APPS_DIR) + '/media/output_files/' + filename, 'lexmaprmediafiles',
                                        filename)
            url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': 'lexmaprmediafiles', 'Key': filename},
                ExpiresIn=86400)
            if job.complete:
                res['download_url'] = url
                res['complete'] = job.complete
                res['expires'] = job.expires
                res['msg'] = 'Job completed.'

            elif not job.complete:
                res['complete'] = job.complete
                res['expires'] = job.expires
                res['msg'] = 'Job still running.'
            if job.err:
                res['error'] = job.err_msg
        return Response(res)
