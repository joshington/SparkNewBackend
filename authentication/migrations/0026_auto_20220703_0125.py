# Generated by Django 2.2 on 2022-07-03 01:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0025_auto_20220702_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 3, 1, 25, 37, 157561)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 3, 1, 25, 37, 157580)),
        ),
    ]
