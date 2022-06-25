# Generated by Django 2.2 on 2022-06-24 15:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_auto_20220624_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 24, 18, 37, 32, 481594)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 24, 18, 37, 32, 481594)),
        ),
    ]