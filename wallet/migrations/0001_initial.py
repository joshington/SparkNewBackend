# Generated by Django 2.2 on 2022-06-25 19:45

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETE', 'Complete'), ('FAILED', 'Failed')], default='PENDING', max_length=8)),
                ('transaction_ref', models.UUIDField(default=uuid.uuid4)),
                ('paid_at', models.DateTimeField(default=datetime.datetime(2022, 6, 25, 22, 45, 20, 84832))),
                ('amount', models.IntegerField()),
                ('category', models.CharField(choices=[('TOP_UP', 'Top Up'), ('WITHDRAW', 'Withdraw')], default='TOP_UP', max_length=8)),
                ('user', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.IntegerField(editable=False)),
                ('payment_id', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='wallet.Payment')),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('balance', models.IntegerField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('latest_transaction', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='wallet_transaction', to='wallet.Transaction')),
                ('owner', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('transfer_reason', models.CharField(default='official', max_length=200)),
                ('transferred_from', models.ForeignKey(db_constraint=False, default=None, on_delete=django.db.models.deletion.CASCADE, related_name='transferred_from', to=settings.AUTH_USER_MODEL)),
                ('transferred_to', models.ForeignKey(db_constraint=False, default=None, on_delete=django.db.models.deletion.DO_NOTHING, related_name='transferred_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='transfer_id',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='wallet.Transfer'),
        ),
    ]
