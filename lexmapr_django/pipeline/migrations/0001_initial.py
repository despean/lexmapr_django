# Generated by Django 2.1.8 on 2019-08-14 20:52

from django.db import migrations, models
import lexmapr_django.pipeline.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PipelineJob',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('complete', models.BooleanField()),
                ('input', models.TextField()),
                ('output', models.TextField()),
                ('expires', models.DateTimeField(default=lexmapr_django.pipeline.models.get_expiry_date)),
            ],
        ),
    ]