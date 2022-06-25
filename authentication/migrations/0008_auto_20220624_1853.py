# Generated by Django 2.2 on 2022-06-24 15:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_auto_20220624_1837'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_created',
            new_name='pin_created',
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 24, 18, 53, 43, 600582)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 24, 18, 53, 43, 600582)),
        ),
    ]