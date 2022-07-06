from django.db import models

from django.db import models,IntegrityError,transaction
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
import datetime
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from datetime import datetime,timedelta,timezone
# Create your models here.

from django.utils import timezone
from wallet.models import*

class UserManager(BaseUserManager):
    use_in_migrations: True
    def create_user(self, uname,phone,email,PIN,password=None):
        if not email:raise ValueError(_('You must provide an email address'))
        if not  phone:raise ValueError(_('You must provide a phone contact'))
        email = self.normalize_email(email)
        user=self.model(uname,phone=phone,email=self.normalize_email(email), PIN=PIN)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, uname, phone,email,PIN):
        user=self.create_user(uname,email,phone,PIN)
        user.is_superuser=True
        user.is_staff=True
        user.save(using=self._db)
        return user

    #fetch all users using


months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

#====since we are making a custom django model
class User(AbstractBaseUser,PermissionsMixin):
    uname = models.CharField(max_length=12,default='@bosa')
    phone = models.CharField(max_length=17,null=False,unique=True,db_index=True)
    email = models.EmailField(max_length=32,unique=True,db_index=True)
    PIN =  models.IntegerField(unique=True,null=True,blank=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(default=datetime.datetime.now())
    pin_created = models.BooleanField(default=False)
    country = models.CharField(max_length=17,default='Uganda')
    now_admin = models.BooleanField(default=False)
    #this is to help me handle regenerating the pin, create new pin


    @property
    def get_month(self):
        return months[self.created_at.date().month - 1]

    @property
    def currency(self):
        pass



    objects=UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']



    #===so if i do user.get_month == gets me the month the user was registered in



    def __str__(self):
        return self.email

    class Meta:
        unique_together = ("PIN","email")

    def get_full_name(self):
        return self.uname

    def get_short_name(self):
        return self.uname

    def has_perm(self,perm,obj=None):
        """Does the user have aspecific permission"""
        return True

    def has_module_perms(self, app_label: str) -> bool:
        """Does the user have permissions to view the app `app_label`"""
        return True

#==now time to do the EmailOTP module

class EmailOTP(models.Model):
    otp = models.IntegerField()
    count = models.IntegerField(default=0, help_text = 'Number of otp_sent')
    validated =  models.BooleanField(default = False,
        help_text = 'If it is true, that means user have validate otp correctly in second API')
    owner = models.ForeignKey(User, related_name='userotp', on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return self.otp


#====working on the admin
class UserAdmin(models.Model):
    email = models.EmailField(unique=True,db_index=True)
    username = models.CharField(max_length=12,default='@admin')
    password = models.CharField(max_length=20)

    def __str_(self):
        return self.username




#=====now here comes the magic of signals
#==task is to send otp when user gives in their phone number and email address
#thus after registering


#====before saving

@transaction.atomic
@receiver(post_save, sender=User)
def create_wallet(sender, instance,created, **kwargs):
    """
        create awallet for every new user
    """
    if created:
        print("testing creating the wallet")
        try:
            transfer = Transfer(
                transferred_to=instance, transferred_from=instance,transfer_reason='Initial Transfer',amount=0
            )
            transfer.save()
            print("saving transfer")
            transaction = Transaction(amount=transfer.amount)
            transfer.save()
            print("saving transaction")
            wallet=Wallet(balance=0, owner=instance, latest_transaction=transaction)
            print("saving wallet..")
            wallet.save()
        except IntegrityError as e:
            raise e