# Generated by Django 2.2 on 2022-07-05 08:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0049_auto_20220705_0826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 8, 32, 21, 77375)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 8, 32, 21, 77394)),
        ),
    ]
