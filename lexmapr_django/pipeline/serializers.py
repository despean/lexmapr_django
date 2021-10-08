from rest_framework import serializers

from lexmapr_django.pipeline.models import PipelineJob


class PipelineJobSerializer(serializers.ModelSerializer):
    class Meta():
        model = PipelineJob
        fields = '__all__'
