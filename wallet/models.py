# from locale import currency
import uuid
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils import timezone
#can use timezone to get after days, months
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

import datetime


class Payment(models.Model):
    Statuses = (
        ('PENDING','Pending'),
        ('COMPLETE', 'Complete'),
        ('FAILED', 'Failed'),
    )
    Categories = (
        ('TOP_UP','Top Up'),
        ('WITHDRAW', 'Withdraw')
    )
    id= models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    status = models.CharField(max_length=8, choices=Statuses,default="PENDING")
    transaction_ref = models.UUIDField(default=uuid.uuid4)
    paid_at = models.DateTimeField(default=datetime.datetime.now())
    amount = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,db_constraint=False)
    category = models.CharField(max_length=8,choices=Categories,default="TOP_UP")


    def __str__(self) -> str:
        return str(self.id)


class Transfer(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    transferred_to = models.ForeignKey(
		settings.AUTH_USER_MODEL,on_delete=models.DO_NOTHING,related_name='transferred_to',db_constraint=False,
		default=None
	)
    transferred_from = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='transferred_from',db_constraint=False,
		default=None
	)
    amount = models.IntegerField()
    transfer_reason = models.CharField(max_length=200,default='official')

    def __str__(self) -> str:
        return str(self.id)


class Transaction(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.IntegerField(editable=False)
    payment_id = models.ForeignKey(Payment,blank=True, on_delete=models.CASCADE, null=True,db_constraint=False)
    transfer_id = models.ForeignKey(Transfer, blank=True,null=True, on_delete=models.CASCADE,db_constraint=False)


    def __str__(self) -> str:
        return str(self.id)



class Wallet(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    balance=models.IntegerField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,db_constraint=False,related_name='user')
    latest_transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE,\
        db_constraint=False,related_name='wallet_transaction')
    created_at = models.DateTimeField(default=datetime.datetime.now(),editable=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self) -> str:
        return str(self.owner)


    @property
    def currency(self):
        if self.owner.country == 'Uganda':
            currency = 'UGX'
        elif self.owner.country == 'Ghana':
            currency = 'GHS'
        elif self.owner.country == 'Nigeria':
            currency = 'NGN'
        elif self.owner.country == 'Arab Emirates':
            currency = 'AED'
        return currency

#====>model for generating profits=====
class Profits(models.Model):
    profit_amount=models.IntegerField()
    payment_ref = models.ForeignKey(Payment,blank=True, on_delete=models.CASCADE, null=True,db_constraint=False)
    created = models.DateTimeField(default=datetime.datetime.now())



    class Meta:
        ordering = ['created']

    def __str__(self) -> str:
        return self.profit_amount



#====model for the card====
class BankAccount(models.Model):
    account_number = models.CharField(blank=False,max_length=12)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,db_constraint=False,related_name='act_owner')
    bank_code = models.CharField(default="044",max_length=20)
    bank = models.CharField(default="Stanbic",max_length=30)
    currency = models.CharField(default="UGX",max_length=3)

    def __str__(self):
        return self.owner

#=====card is actually for UAE users


class BankCard(models.Model):
    cardno=models.CharField(max_length=20)
    cvv = models.CharField(max_length=20)
    currency=models.CharField(default="UGX",max_length=10)
    expiry_month=models.CharField(max_length=20)
    expiryyear=models.IntegerField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,db_constraint=False,related_name='user_card')

    def __str__(self):
        return self.owner


#=====since virtual accounts are good let me just add them for nigerian users===
class VirtualAccount(models.Model):
    bvn = models.CharField(max_length=30,blank=False)
    email=models.EmailField(blank=False)
    txRef = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)#since we can use it to trace the virtual account
    is_permanent=models.BooleanField(default=False)
    narration=models.CharField(default='@sparkuser',max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,db_constraint=False,related_name='user_virtual_acct')


    def __str__(self) -> str:
        return self.bvn

    #==awesome user virtual account created succesffully, not hard i think=