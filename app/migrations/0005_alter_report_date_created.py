# Generated by Django 4.2.7 on 2024-10-16 12:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_report_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 16, 12, 51, 15, 686325, tzinfo=datetime.timezone.utc), verbose_name='Дата создания'),
        ),
    ]