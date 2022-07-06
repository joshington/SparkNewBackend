from operator import add
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
from .models import Payment, Transaction,Wallet,Profits
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


rave = Rave("FLWPUBK-253d6258de134d39d454c04310656340-X","FLWSECK-0ff584946aa70186e0d1bc307b408725-X", usingEnv=False, production=True)
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


class TopUp(APIView):
    """
        essence is to topup on the wallet
    """
    serializer_class = TopUpSerializer

    @transaction.atomic
    def post(self,request,*args, **kwargs):
        phone=request.data.get('phone',False)
        amount=request.data.get('amount',False)
        user = User.objects.filter(phone__iexact=phone).first()
        if user:
            try:
                make_momo_payment(amount=amount,phonenumber=phone,user=user)
                return Response({
                    'status':True,
                    'detail':'Top up initiated'
                })
            except Exception as e:
                print(e)
                return Response({
                    'status':False,
                    'detail':'Top up Failed'
                })
        else:
            return Response({'status':False,'detail':'User not authenticated'})

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
        queryset = User.objects.filter(uname__icontains=username)

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
            #get sender balance
            sender_balance = wallet_user.balance
            #==get the recipient now=====
            receiver_list = User.objects.filter(uname=recipient)
            receiver = receiver_list.first()
            if receiver.is_verified:
                #user can only receive if they are verified
                if sender_balance*0.5 > minimum_balance and sender_balance - int(amount) > minimum_balance:
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


class WithdrawView(APIView):
    def post(self, request, *args, **kwargs):
        """
            task is to test the transfer endpoint on flutterwave
            256704372213
        """
        #===first get the balance of the top user to proceed====

        user_email = request.query_params['email']
        amount = request.query_params['amount']

        charge = 500; minimum_balance = 2000

        #==basis
        try:
            user_targ = User.objects.get(email=user_email)
            wallet_user = Wallet.objects.get(owner=user_targ)
            #get sender balance
            sender_balance = wallet_user.balance
            if user_targ.is_verified:
                if user_targ.country in mm_countries:
                    if sender_balance*0.5 > minimum_balance and sender_balance - (int(amount) + charge) > minimum_balance:
                        #====first deduct then send ===, i think thats how the logic works
                        #===first deduct the dimes then complete

                        #instantiating payment but still pending
                        try:
                            sender_balance -=  int(amount)
                            wallet_user.save()
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
                            #====saved the withdraw to account as successful

                            #===its time to create and save the profit model to the db
                            profit = Profits(
                                profit_amount=charge,
                                payment_ref=new_payment
                            )
                            profit.save()
                            return Response({
                                'status':True,
                                'message':'withdraw to account successful',

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



#======withdraw to non spark user is alittle different only difference is to provide phone number
class SendNonSparkView(APIView):
    def post(self,request,*args, **kwargs):
        email = request.query_params['email']#gottern the email now
        rec_country = request.query_params['country']
        amount = request.query_params['amount']
        rec_phone = request.query_params['phone']

        charge = 500; minimum_balance = 2000
        try:
            user_targ=User.objects.get(email=email)
            if user_targ.is_verified:
                    if rec_country in mm_countries:
                        try:
                            wallet_user = Wallet.objects.get(owner=user_targ)
                            sender_balance = wallet_user.balance
                            if sender_balance*0.5 > minimum_balance and sender_balance - (int(amount) + charge) > minimum_balance:
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
                                        profit_amount=charge,
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
        balance = wallet_user.balance
        owner   = now_user.uname
        return Response({'status':True,'balance':balance,'owner':owner,'phone':now_user.phone}, status=status.HTTP_200_OK)

