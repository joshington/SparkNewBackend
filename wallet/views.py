from operator import add
import uuid
from django.shortcuts import render
# import django_filters.rest_framework
from rest_framework import generics, status,views
from rest_framework.views import APIView
# Create your views here.
from rest_framework.response import Response

from rest_framework import authentication,permissions

from django.db import models

import json,base64 #we want to decode the token


import json ,re
from uuid import UUID
from django.db import transaction
from authentication.models import*

from .serializers import*
from .models import Payment, Transaction,Wallet,Profits,BankCard
from .utils.balance import balance as get_balance
from .utils.rave import make_momo_payment
from .utils.top_up import top_up
from .utils.withdraw import withdraw

from authentication.models import User

from rave_python import Rave,  Misc, RaveExceptions


#importing ent variables

# Initialise environment variables
from dotenv import load_dotenv
import os

load_dotenv()


# RAVE_SECRET_KEY = os.environ["secret_key"]
# RAVE_PUBLIC_KEY = os.environ["public_key"]
# DEFAULT_PAYMENT_EMAIL = os.environ["default_email"]

# secret_key="FLWSECK_TEST-e0cbc06d58428b734f5caa144be6cbb7-X"
# public_key="FLWPUBK_TEST-0848d18635e3b1ef8e9a17c0473b1801-X"
# MerchantID=5799821


rave = Rave("FLWPUBK-253d6258de134d39d454c04310656340-X","FLWSECK-0ff584946aa70186e0d1bc307b408725-X", usingEnv=False,production=True)
#os.getenv("SEC_KEY")
# rave = Rave(RAVE_PUBLIC_KEY, RAVE_SECRET_KEY, usingEnv = False)


#====flutterwave part only============
def handle_successful_payment(data):
    transaction_ref = data['txRef']
    payment=Payment.objects.get(transaction_ref=transaction_ref)

    if payment.category == Payment.Categories.TOP_UP:
        top_up(payment.user.phone,payment.amount)
    payment.status = Payment.Statuses.COMPLETE
    payment.save()

def key_exists(key,dict,label):
    if not key in dict:
        raise Exception("'{}' must exist in '{}'".format(key,label))


def required_fields(dict, required, label):
    [key_exists(i,dict,label) for i in required]


#=====write func to get the withdraw limit======
def get_withdraw_limit(currency):
    return {
        'UGX':3500000,
        'GHS':7000,
        'NGN':390494
    }[currency]





class GetBalance(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class=GetBalanceSerializer

    @transaction.atomic
    def get(self, request):
        phone=request.data.get('phone',False)

        user_target = User.objects.filter(phone__iexact=phone).first()
        if user_target:
            try:
                balance = get_balance(user_target.phone,user_target)
                print("passed this step")
                return Response({'status':True,'balance':balance}, status=status.HTTP_200_OK)
            except Exception as e:
                string_exception = str(e)
                return Response({'error':string_exception}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status':False,'detail':'Balance not returned'},status=status.HTTP_400_BAD_REQUEST)




class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,UUID):
            #if obj is uuid we simpley return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self,obj)

#====view to handle choice of apackage

mm_countries = ['Uganda','Ghana']

curency_account_dict = {"UGX":"MPS","GHS":["MTN","TIGO","VODAFONE","AIRTEL"]}


def top_mthd(country,payload):
    return {
        'Uganda':rave.UGMobile.charge(payload),
        'Ghana':rave.GhMobile.charge(payload)
    }[country]


class TopUpMomo(APIView):
    """
        essence is to topup on the wallet,
        on frontend give options of mobile money or bank
        ==> if user country in mobile money countries, and user selected mobile money proceed with topup of mobile money
        else return response mobile money not supported in country,
        if nigeria go ahead and use virtual cards, else go ahead and use bank, remember the get banks api basing on the country
        ask user to choose from the banks.
    """
    #=======instead use request params to get the input=====
    @transaction.atomic
    def post(self,request,*args, **kwargs):
        #==just use request params ====
        email  = request.query_params['email']
        amount = request.query_params['amount']
        #gonna pick up the phone number from the user
        try:
            user_targ = User.objects.get(email=email)
            #since every country has a different charge method
                #first inquire whether country is in the mm countries
            if user_targ.country in mm_countries:
                payload = make_momo_payment(amount=int(amount),country=user_targ.country,phonenumber=user_targ.phone,user=user_targ)
                res = top_mthd(country=user_targ.country, payload=payload)
                try:
                    return Response(res)
                except RaveExceptions.TransactionChargeError as e:
                    return Response({
                        'status':False,
                        'error':e.err,
                        'ref': e.err["flwRef"]
                    })
            else:
                return Response({
                    'status':False,
                    'message':'Country not support, use bank'
                })
        except User.DoesNotExist:
            return Response({
                'status':False,
                'message':'User Not Found,Register'
            })


class TopUpAccount(APIView):
    """
        essence is to top up using account number from the bank
    """
    def post(self):
        pass


#finding======all the required the transactions from the wallet
class Last7Transactions(APIView):
    def get(self, request):
        #===have to fist check that user is authenticated
        # request = self.context.get("request")
        # if request and hasattr(request, "user"):
        user=self.request.user
        print(user.id)
        all_payments = Payment.objects.filter(category='TOP_UP')
        #===since its a list its time to iterate
        #use enumerate to return
        days_of_week = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        payment_array = [(days_of_week[payment.paid_at.weekday()],payment.amount) for payment in all_payments]

        #now after getting the payment array
        return Response({'status':True,'last7transactions':payment_array},status=status.HTTP_200_OK)





#===========search for users========
class SparkUsersView(APIView):
    serializer_class = SparkUserSerializer
    def get(self,request,*args,**kwargs):
        username=self.request.query_params.get('uname')

        email = self.request.query_params.get('email')
        #get the users uname from the email now=====
        #====give in the user email====
        owner_user = User.objects.get(email=email)
        queryset = User.objects.filter(uname__icontains=username).exclude(uname=owner_user.uname)

        all_users = [user.uname for user in queryset]



        #==now just return the users======
        return Response({'status':True,'users':all_users}, status=status.HTTP_200_OK)


#====sending money to the user chosen======



#=====this is for the
class TransPerMonth(APIView):
    def get(self,request):
        """
            target of endpoint is to return transactions per month
        """
        #all_payments=
        pass

class Withdraw(APIView):
    serializer_class = WithdrawSerializer

    def post(self, request):
        phone = request.data.get('phone_number',False)
        amount=request.data.get('amount',False)
        user=User.objects.filter(phone=phone)

        print(user)
        if user is not None:
            try:
                print("now have enetered the loop")
                print("next is to trigger the withdraw")
                print(user)
                print(user.phone)
                #getting phone first
                withdraw(user.phone, amount,user)
                print("what next after the withdraw=====")
                return Response({
                    'status':True,
                    'detail':'Amount withdrawn successfully from wallet'
                })
            except Exception as e:
                string_exception = str(e)
                return Response({
                    'status':False,
                    'detail':'Error during withdraw from wallet'
                })
        else:
            return Response({
                'status':False,
                'detail':'Phone number not registered on the platform'
            })




#======send to a flutterwave =====account
#===similar to a withdraw
class SendToAccountView(APIView):
    def post(self, request, *args, **kwargs):
        email  = request.query_params['email']#gottern the email now
        amount =  request.query_params['email']#gottern the email now
        recipient = request.query_params['recipient']#gottern the email now


        #===set my minimum balance as 2000
        minimum_balance = 2000
        if recipient and amount and email:
            sender = User.objects.get(email=email)
            wallet_user = Wallet.objects.get(owner=sender)

            minimum_balance = get_minimum(wallet_user.currency)
            withdraw_limit = get_withdraw_limit(wallet_user.currency)
            #get sender balance
            sender_balance = wallet_user.balance
            #==get the recipient now=====
            receiver_list = User.objects.filter(uname=recipient)
            receiver = receiver_list.first()
            if receiver.is_verified:
                #user can only receive if they are verified
                if sender_balance*0.5 > minimum_balance and sender_balance - int(amount) > minimum_balance and int(amount) < withdraw_limit:
                    #==first reduce the sender's balance
                    sender_balance  -=  int(amount)
                    wallet_user.save()
                    sender.save()#===chop the senders's balance straight away
                    #create a Transaction
                    new_payment=Payment(status='PENDING',amount=int(amount),user=sender,
                        category='WITHDRAW'
                    )
                    #==i dont want to save it now
                    receiver_wallet = Wallet.objects.get(owner=receiver)
                    #==increase his wallet balance
                    receiver_wallet.balance += int(amount)
                    receiver_wallet.save()
                    new_payment.status='COMPLETE'
                    new_payment.save()
                    #i think thats it the sending is done
                    #===since a transction was carried out
                    # transaction = Transaction(amount=int(amount),payment_id=new_payment)
                    return Response({
                        'status':True,
                        'message':'sent {0} to {1} successfully'.format(amount, recipient)
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'status':False,'message':'Low balance please recharge'})
            else:
                return Response({'status':False,'message':'Recipient is not verified'})
        else:
            return Response({
                'status':False,
                'message':'Provide all detail'
            })



class WebHook(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            required_fields(request.headers, ['verify-hash'],'request headers')
            required_fields(request.data, ['txRef'], 'request body')

            hash =request.headers['verify-hash']
            pass
        except:
            pass


def format_phone_number(phone_number):
    if re.search(r"\A\+2567\d{8}\Z",phone_number):
        return phone_number[1:]
    elif re.search(r"\A07\d{8}\Z",phone_number):
        return "256" + phone_number[1:]


def transfer_money_to_phone(phone, amount,username="Unknown User"):
    details =  {
        "account_bank":"MPS",
		"account_number":format_phone_number(phone),
		"amount":amount,
        "currency":"UGX",
        "beneficiary_name":username,
        "meta":{
            "sender": "Flutterwave Developers",
            "sender_country": "UGA",
            "mobile_number": "256760810134"
        }
    }
    res = rave.Transfer.initiate(details)


#===account_number => mobile number on account with code like 233
#beneficiary name => just make this default

#===i want to test this transfer cz man its not working properly=======
#==but actually ask them to first confirm the phone number
#so ask for it


#=====format the phone number basing on the coutry ===so actually
def format_phone_number(phone_number):
    if re.search(r"\A\+2567\d{8}\Z",phone_number):
        return phone_number[1:]
    elif re.search(r"\A07\d{8}\Z",phone_number):
        return "256" + phone_number[1:]
#=====actually

#===just  use a function to automate adding country code to the phone=====
def add_code_phone(country,phone):
    return {
        'Uganda':'256'+phone[1:],
        'Kenya':'254'+phone[1:],
        'Tanzania':'255'+phone[1:],
        'Rwanda':'250'+phone[1:],
        'Zambia':'260'+phone[1:],
        'Ghana':'233'+phone[1:],
        'Cameroon':'237'+phone[1:],
        "Cote d'Ivoire":'225'+phone[1:],

    }[country]
#task is at hand is t


mm_countries = ["Rwanda","Tanzania","Uganda","Zambia","Kenya","Ghana","Cameroon","Cote d'Ivoire"]

#====take in phone number and country
def format_phone_number(phone_number,country):
    if phone_number and country:
        if country in mm_countries:
            if country == 'Uganda':
                if re.search(r"\A\+2567\d{8}\Z",phone_number):
                    return phone_number[1:]
                elif re.search(r"\A07\d{8}\Z",phone_number):
                    return add_code_phone(country,phone_number)
            elif country == 'Kenya':
                if re.search(r"\A\+2547\d{8}\Z",phone_number):
                    return phone_number[1:]
                elif re.search(r"\A07\d{8}\Z",phone_number):
                    return add_code_phone(country,phone_number)
            elif country == 'Tanzania':
                if re.search(r"\A\+2557\d{8}\Z",phone_number):
                    return phone_number[1:]
                elif re.search(r"\A07\d{8}\Z",phone_number):
                    return add_code_phone(country,phone_number)




#transfer to user


#=====function to help format the account bank
def get_account_bank(country):
    home_countries = ["Rwanda","Tanzania","Uganda","Zambia"]
    account_bank = "MPS"
    if country in home_countries:
        account_bank = "MPS"
    elif country == "Kenya":
        account_bank = "MPX"
    elif country == "Ghana":
        account_bank = "MTN"
    elif country == "Cameroon" or country == "Cote d'Ivoire":
        account_bank = "FMM"

    return account_bank



def get_currency(country):
    if country == "Rwanda":
        currency = "RWF"
    elif country == "Tanzania":
        currency = "TZS"
    elif country == "Uganda":
        currency = "UGX"
    elif country == "Zambia":
        currency = "ZMW"
    elif country == "Kenya":
        currency = "KES"
    elif country == "Ghana":
        currency = "GHS"
    elif country == "Cameroon":
        currency = "XAF"
    elif country =="Cote d'Ivoire":currency = "XOF"


#===get all rates===
class GetRates(APIView):
    def get(self, request, *args, **kwargs):
        """returns all supported currencies"""
        res2= rave.Transfer.getFee()
        return Response({
            "status":True,
            "message":"All rates",
            "rates":res2
        })



#=====process balance is the basis for all cashouts====
#===get the top balance
class GetBalance(APIView):
    def get(self, request, *args, **kwargs):
        res2= rave.Transfer.getFee()
        return Response({
            'status':True,
            'bal_data':res2
        })
#====this from the rave acount

def get_minimum(currency):
    return {
        'NGN':220,
        'UGX':2000,
        'GHS':5,
        'AED':5
    }[currency]

class WithdrawView(APIView):
    def post(self, request, *args, **kwargs):
        """
            task is to test the transfer endpoint on flutterwave
            256704372213
        """
        #===first get the balance of the top user to proceed====

        user_email = request.query_params['email']
        amount = request.query_params['amount']

        perc_charge = 0.014
        #the charge is to be 1.4%


        #==basis
        try:
            user_targ = User.objects.get(email=user_email)
            wallet_user = Wallet.objects.get(owner=user_targ)
            #get sender balance
            sender_balance = wallet_user.balance
            #get the minim balance
            minimum_balance = get_minimum(wallet_user.currency)
            withdraw_limit = get_withdraw_limit(wallet_user.currency)
            if user_targ.is_verified:
                if user_targ.country in mm_countries:
                    if sender_balance*0.5 > minimum_balance and int(amount) < withdraw_limit  and sender_balance - (int(amount) + (perc_charge*int(amount))) > minimum_balance:
                        #====first deduct then send ===, i think thats how the logic works
                        #===first deduct the dimes then complete

                        #instantiating payment but still pending
                        try:

                            #save the wallet

                            new_payment=Payment(status='PENDING',amount=int(amount),user=user_targ,
                                category='WITHDRAW'
                            )
                            new_payment.save()
                            details = {
                                "account_bank": get_account_bank(user_targ.country),
                                "account_number": format_phone_number(user_targ.phone,user_targ.country),
                                "amount": int(amount),
                                "currency": get_currency(user_targ.country),
                                "beneficiary_name": user_targ.uname,
                                "meta": [
                                    {
                                        "sender": "Flutterwave Developers",
                                        "sender_country": "UG",
                                        "mobile_number": "256704372213"
                                    }
                                ],
                            }
                            res=rave.Transfer.initiate(details)
                            new_payment.status='COMPLETE'
                            new_payment.save()
                            sender_balance -=  int(amount)
                            wallet_user.save()
                            #====saved the withdraw to account as successful

                            #===its time to create and save the profit model to the db
                            profit = Profits(
                                profit_amount=perc_charge*int(amount),
                                payment_ref=new_payment
                            )
                            profit.save()
                            return Response({
                                'status':True,
                                'message':'withdraw to mobile money successful',

                            },status=status.HTTP_200_OK)
                        except RaveExceptions.IncompletePaymentDetailsError as e:
                            sender_balance = sender_balance
                            wallet_user.save()
                            return Response({
                                'status':False,
                                'message':'Transaction Error'
                            })
                    else:
                        return Response({
                            'status':False,
                            'message':'Insufficient balance'
                        })
                else:
                    return Response({
                        'status':False,
                        'message':'Mobile money not support in country'
                    })
            else:
                return Response({
                    'status':False,
                    'message':'User is not verified'
                })

        except User.DoesNotExist:
            return Response({
                'status':False,
                'message':'User not found'
            })

#======check PIN
#===i think we can use the Login PIN view
class CheckPINView(APIView):
    def post(self,request,*args,**kwargs):
        email = request.query_params['email']#gottern the email now
        PIN = request.query_params['PIN']

        try:
            user = User.objects.get(email=email)
            if user.PIN == int(PIN):
                return Response({
                    'status':True,
                    'message':'User PIN matches'
                })
            else:
                return Response({
                    'status':False,
                    'message':'Enter correct PIN'
                })
        except User.DoesNotExist:
            return Response({
                'status':False,
                'message':'User Not Found'
            })

easy_countries = ["Uganda","Ghana","Nigeria"]
#=====send to bank account=====
class SelfWithdrawBank(APIView):
    def post(self,request,*args,**kwargs):
        """target is to get the details so that user can withdraw from bank but get user details
            get the email of the user to confirm that he is not foreign.
        """
        email = request.query_params['email']#gottern the email now
        amount = request.query_params['amount']
        # rec_branch = request.query_params['bank branch']
        #===here i dont need the rec_branch since its the same as registered
        try:
            _usernow  = User.objects.select_related().get(email=email)
            if _usernow and _usernow.is_verified:
                #have to check the user balance from their wallet
                wallet_user = Wallet.objects.get(owner=_usernow)
                #==get the account number using select_related====
                try:
                    user_account = BankAccount.objects.get(owner=_usernow)
                    if user_account:

                        #now get the account number
                        account_number = user_account.account_number
                        #====bank code as well===
                        bank_code = user_account.bank_code
                        if user_account and _usernow.country in easy_countries:
                            wallet_balance = wallet_user.balance

                            perc_charge = 0.014
                            #get the minim balance
                            minimum_balance = get_minimum(wallet_user.currency)
                            withdraw_limit = get_withdraw_limit(wallet_user.currency)
                            #========above fetches the withdraw limit  of the user=======
                            if amount:
                                if wallet_balance*0.5 > minimum_balance and int(amount) < withdraw_limit and wallet_balance - (int(amount) + (perc_charge*int(amount))) > minimum_balance:
                                    new_payment=Payment(status='PENDING',amount=int(amount),user=_usernow,
                                        category='WITHDRAW'
                                    )
                                    new_payment.save()
                                    #start the process, get dest branch code
                                    details = {
                                        "account_bank":bank_code,
                                        "account_number": account_number,
                                        "amount": int(amount),
                                        "narration": "Test GHS bank transfers",
                                        "currency": wallet_user.currency,
                                        "destination_branch_code": bank_code,
                                        "beneficiary_name": "recipient"
                                    }
                                    res = rave.Transfer.initiate(details)
                                    new_payment.status = 'COMPLETE'
                                    new_payment.save()
                                    wallet_balance -= int(amount)
                                    wallet_user.save()
                                    #saving the profits===
                                    profit = Profits(
                                        profit_amount=perc_charge*int(amount),
                                        payment_ref=new_payment
                                    )
                                    profit.save()
                                    return Response({
                                        'status':True,
                                        'message':'withdraw to Bank successful',

                                    },status=status.HTTP_200_OK)
                                else:
                                    return Response({
                                        'status':False,
                                        'message':'Low Balance, please Topup'
                                    })
                            else:
                                return Response({
                                    "status":False,
                                    "message":"Enter amount"
                                })
                        else:
                            return Response({
                                "status":False,
                                "message":"Add Account details in profile"
                            })
                    else:
                        return Response({
                            "status":False,
                            "message":"User Bank Account not found, add"
                        })
                except BankAccount.DoesNotExist:
                    return Response({
                        "status":False,
                        "message":"Bank details Not Found, Add"
                    })
            else:
                return Response({
                    "status":False,
                    "message":"User not verified"
                })
                #===pick it from their bank account======
                #let users first add their bank account.
                #pick it from the
        except User.DoesNotExist:
            return Response({
                'status':False,
                'message':'email not found'
            })



#=====mthd for generating the reference=====
def generate_transaction_reference():
    ref =  uuid.uuid4()
    return ref


#===now when sending money to a user using their account number========
#====okay for this the user canbe similar but still i need their bank branch details, bank code to say, country
class SendToBankUser(APIView):
    def post(self, request, *args,**kwargs):
        email = request.query_params['email']#gottern the email now
        rec_country = request.query_params['country']#cz this helps me get the bank code of the users bank
        rec_acct_number = request.query_params['receiver_account_number']
        rec_branch_code = request.query_params['receiver_branch_code']
        amount = request.query_params['amount']
        rec_currency = request.query_params['receiver_currency']
        rec_name  = request.query_params['receiver_name']

        #====cz  for countries ======
        perc_charge = 0.014

        if email and rec_country and rec_acct_number and rec_branch_code and amount and rec_currency:
            #get the user basing on the email provided.
            user_targ = User.objects.select_related().get(email=email)
            if user_targ.is_verified:
                wallet_now = Wallet.objects.get(owner=user_targ)
                #get the minim balance
                minimum_balance = get_minimum(wallet_now.currency)
                #after getting the user's wallet now findout their balance
                withdraw_limit = get_withdraw_limit(wallet_now.currency)
                user_balance = wallet_now.balance

                #==get the account number using select_related====
                try:
                    user_account = BankAccount.objects.get(owner=user_targ)
                    if user_account:
                        #now get the account number
                        account_number = user_account.account_number
                        #====bank code as well===
                        bank_code = user_account.bank_code
                        if user_balance*0.5 > minimum_balance and int(amount) < withdraw_limit and  user_balance - (int(amount) + (perc_charge*int(amount))) > minimum_balance:
                            if rec_country == 'Nigeria':
                                #why i pickd out nigeria its ecause the payload changes abit
                                #==start and instantiate the Payment object,
                                new_payment=Payment(status='PENDING',amount=int(amount),user=user_targ,
                                    category='WITHDRAW'
                                )
                                new_payment.save()
                                details = {
                                    "account_bank": rec_branch_code,
                                    "account_number": rec_acct_number,
                                    "amount": int(amount),
                                    "narration": "Payment for things",
                                    "currency": rec_currency,
                                    "reference": generate_transaction_reference(),
                                    "callback_url": "https://webhook.site/b3e505b0-fe02-430e-a538-22bbbce8ce0d",
                                    "debit_currency": wallet_now.currency
                                }
                                res = rave.Transfer.initate(details)
                                #===have to confirm that the transfer was successful======
                                new_payment.status = 'COMPLETE'
                                new_payment.save()
                                user_balance -= int(amount)
                                wallet_now.save()
                                    #saving the profits===
                                profit = Profits(
                                    profit_amount=perc_charge*int(amount),
                                    payment_ref=new_payment
                                )
                                profit.save()
                                return Response(res, status=status.HTTP_200_OK)
                            elif rec_country  == "Uganda" or rec_country == "Ghana":
                                new_payment=Payment(status='PENDING',amount=int(amount),user=user_targ,
                                    category='WITHDRAW'
                                )
                                new_payment.save()
                                details = {
                                    "account_bank": rec_branch_code,
                                    "account_number": rec_acct_number,
                                    "amount": int(amount),
                                    "narration": "send account",
                                    "currency": rec_currency,
                                    "destination_branch_code":rec_branch_code,
                                    "beneficiary_name":rec_name
                                }
                                res = rave.Transfer.initate(details) #now actually initiating the transfer here
                                #have to verify that actually the transfer was complete
                                new_payment.status = 'COMPLETE'
                                new_payment.save()
                                user_balance -= int(amount)
                                wallet_now.save()
                                profit = Profits(
                                    profit_amount=perc_charge*int(amount),
                                    payment_ref=new_payment
                                )
                                return Response(res, status=status.HTTP_200_OK)
                        else:
                            return Response({
                                "status":False,
                                "message":"Low balance, please recharge"
                            })
                    else:
                        return Response({
                            "status":False,
                            "message":"Account Not Found"
                        })
                except BankAccount.DoesNotExist:
                    return Response({
                        "status":False,
                        "message":"User Account Not Found,add"
                    })
            else:
                return Response({
                    "status":False,
                    "message":"User was not verified"
                })

        else:
            return Response({
                "status":False,
                "message":"Provide all details"
            })













#======withdraw to non spark user is alittle different only difference is to provide phone number
class SendNonSparkView(APIView):
    def post(self,request,*args, **kwargs):
        email = request.query_params['email']#gottern the email now
        rec_country = request.query_params['country']
        amount = request.query_params['amount']
        rec_phone = request.query_params['phone']

        minimum_balance = 2000;perc_charge = 0.014
        try:
            user_targ=User.objects.get(email=email)
            if user_targ.is_verified:
                    if rec_country in mm_countries:
                        try:
                            wallet_user = Wallet.objects.get(owner=user_targ)
                            sender_balance = wallet_user.balance

                            minimum_balance = get_minimum(wallet_user.currency)
                            withdraw_limit = get_withdraw_limit(wallet_user.currency)

                            if sender_balance*0.5 > minimum_balance and int(amount) < withdraw_limit and sender_balance - (int(amount) + (perc_charge*amount)) > minimum_balance:
                                try:
                                    sender_balance -=  int(amount)
                                    wallet_user.save()
                                    #save the wallet

                                    new_payment=Payment(status='PENDING',amount=int(amount),user=user_targ,
                                        category='WITHDRAW'
                                    )
                                    new_payment.save()
                                    details = {
                                        "account_bank": get_account_bank(rec_country),
                                        "account_number": format_phone_number(rec_phone,rec_country),
                                        "amount": int(amount),
                                        "currency": get_currency(user_targ.country),
                                        "beneficiary_name": "recipient",
                                        "meta": [
                                            {
                                                "sender": "Flutterwave Developers",
                                                "sender_country": "UG",
                                                "mobile_number": "256704372213"
                                            }
                                        ],
                                    }
                                    res=rave.Transfer.initiate(details)
                                    new_payment.status='COMPLETE'
                                    new_payment.save()
                                    #==save the profits made====
                                    profit = Profits(
                                        profit_amount=(perc_charge*int(amount)),
                                        payment_ref=new_payment
                                    )
                                    profit.save()
                                    #==saving the Profits model to the database
                                    return Response({
                                        'status':True,
                                        'message':'sent to {} successful'.format(rec_phone),

                                    },status=status.HTTP_200_OK)
                                except RaveExceptions.IncompletePaymentDetailsError as e:
                                    sender_balance = sender_balance
                                    wallet_user.save()
                                    return Response({
                                        'status':False,
                                        'message':'Transaction Error'
                                    })
                            else:
                                return Response({
                                    'status':False,
                                    'message':'Insufficient balance'
                                })
                        except Wallet.DoesNotExist:
                            return Response({
                                'status':False,
                                'message':'User wallet not found'
                            })
                    else:
                        return Response({
                            'status':False,
                            'message':'Mobile money not supported '
                        })
            else:
                return Response({
                    'status':False,
                    'message':'User is not verified'
                })
        except User.DoesNotExist:
            return Response({
                'status':False,
                'message':'User not found'
            })





class WalletTopUpSuccess(APIView):
    def post(self,request,*args, **kwargs):
        email = request.query_params['email']
        amount = request.query_params['amount']

        try:
            targ = User.objects.get(email=email)
            if targ and targ.is_verified:
                user_wallet = Wallet.objects.get(owner=targ)
                if user_wallet:
                    if amount:
                        balance = user_wallet.balance
                        balance +=  int(amount)
                        user_wallet.save()#==have to save it to the db
                        #==create the payment====
                        new_payment = Payment(
                            status='COMPLETE',
                            amount=int(amount),
                            user=targ,
                            category='TOP_UP'
                        )
                        new_payment.save()
                        return Response({'status':True,'message':'Top up successful'})
                    else:
                        return Response({
                            'status':False,
                            'message':'Amount missing'
                        })
                else:
                    return Response({
                        'status':False,
                        'message':'Cant find user wallet'
                    })
            else:
                return Response({
                    'status':False,
                    'message':'User email not verified'
                })
        except User.DoesNotExist:
            return Response({'status':False,'message':'User not Found'})


#===view to return the user details


class UserWalletDetails(APIView):
    def get(self,request,*args, **kwargs):
        """get the user details for the wallet
        """
        email = request.query_params['email']#gottern the email now
        now_user=User.objects.get(email=email)
        wallet_user=Wallet.objects.get(owner=now_user)
        #print(request.query_params)
        #print(request.query_params['email'])
        #wallet_balance = wallet_user.balance
        try:
            account = BankAccount.objects.get(owner=now_user)
            if account:
                account_no = account.account_number
                bank_code  = account.bank_code
            else:
                return
        except BankAccount.DoesNotExist:
            account_no = 0;bank_code = 0



        balance = wallet_user.balance
        owner   = now_user.uname
        currency = wallet_user.currency
        withdraw_limit = get_withdraw_limit(currency)
        return Response({
            'status':True,
            'account_no':account_no,
            'bank_code':bank_code,
            'balance':balance,
            'owner':owner,
            'phone':now_user.phone,
            'currency':currency,
            'with_limit':withdraw_limit,
            'country':now_user.country,
            'pin':now_user.PIN,
            }, status=status.HTTP_200_OK)


#====ish at hand is to add the card details now====
class Addcard(APIView):
    def post(self,request, *args,**kwargs):
        """
            add card for the user, mostly for uae users
        """
        #====have to first get the user adding the card=====
        email = request.query_params['email']
        cardno= request.query_params['cardno']
        cvv=request.query_params['cvv']
        currency=request.query_params['currency']
        expiry_month=request.query_params['expiry_month']
        expiryyear=request.query_params['expiryyear']


        if email and cardno and cvv and currency and expiry_month and expiryyear :
            user_now  = User.objects.select_related().get(email=email)
            if user_now and user_now.is_verified:
                #go ahead and add the card
                newcard = BankCard(
                    cardno=cardno,
                    cvv=cvv,
                    currency=currency,
                    expiry_month=expiry_month,
                    expiryyear=expiryyear,
                    owner=user_now
                )
                newcard.save()
                #after saved successfully u shud return aresponse to the user
                return Response({
                    "status":True,
                    "message":"card added successfully"
                })
            else:
                return Response({
                    "status":False,
                    "message":"User not verified"
                })
        else:
            return Response({
                "status":False,
                "message":"Details not provided"
            })






