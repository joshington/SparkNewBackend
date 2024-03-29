# Generated by Django 2.2 on 2022-06-24 07:38

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('uname', models.CharField(default='@bosa', max_length=12)),
                ('phone', models.CharField(db_index=True, max_length=17, unique=True)),
                ('email', models.EmailField(db_index=True, max_length=32, unique=True)),
                ('PIN', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2022, 6, 24, 10, 38, 11, 500141))),
                ('updated_at', models.DateTimeField(default=datetime.datetime(2022, 6, 24, 10, 38, 11, 500141))),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'unique_together': {('PIN', 'email')},
            },
        ),
        migrations.CreateModel(
            name='EmailOTP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.CharField(blank=True, max_length=4, null=True)),
                ('count', models.IntegerField(default=0, help_text='Number of otp_sent')),
                ('validated', models.BooleanField(default=False, help_text='If it is true, that means user have validate otp correctly in second API')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='userotp', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
