# Generated by Django 5.0.7 on 2024-08-08 09:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0006_alter_location_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='Date',
            field=models.DateField(verbose_name=datetime.datetime(2024, 8, 8, 9, 51, 21, 391266, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='territorycollectionreport',
            name='Date',
            field=models.DateField(verbose_name=datetime.datetime(2024, 8, 8, 9, 51, 21, 391266, tzinfo=datetime.timezone.utc)),
        ),
    ]
