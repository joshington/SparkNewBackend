# Generated by Django 2.2 on 2022-06-24 14:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_auto_20220624_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailotp',
            name='otp',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 24, 17, 40, 30, 885110)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 24, 17, 40, 30, 885110)),
        ),
    ]
