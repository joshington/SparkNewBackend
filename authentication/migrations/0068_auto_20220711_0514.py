# Generated by Django 2.2 on 2022-07-11 02:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0067_auto_20220711_0448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailotp',
            name='initial',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 11, 5, 14, 36, 957099)),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 11, 5, 14, 36, 957099)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 11, 5, 14, 36, 957099)),
        ),
    ]