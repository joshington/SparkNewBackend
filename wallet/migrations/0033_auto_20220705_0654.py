# Generated by Django 2.2 on 2022-07-05 06:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0032_auto_20220704_0624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paid_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 6, 54, 12, 275655)),
        ),
        migrations.AlterField(
            model_name='profits',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 6, 54, 12, 277680)),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 6, 54, 12, 277192), editable=False),
        ),
    ]