# Generated by Django 5.0.7 on 2024-08-08 10:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0009_alter_location_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='check_in_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='location',
            name='locations_visited',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='territorycollectionreport',
            name='Date',
            field=models.DateField(verbose_name=datetime.datetime(2024, 8, 8, 10, 4, 9, 157643, tzinfo=datetime.timezone.utc)),
        ),
    ]
