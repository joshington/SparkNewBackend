from calendar import month
from collections import Counter
from unicodedata import category
from django.shortcuts import render
from django.db.models import Avg,Sum
from rest_framework import generics, status,views
from rest_framework.views import APIView
from rest_framework import serializers
# Create your views here.
from rest_framework.response import Response
from .serializers import*
from .models import*
from wallet.models import*

import string
import random
from .utils import Util

def get_ottp():
    key = random.randint(999,9999)
    return key
    # if email:
    #     key = random.randint(999,9999)
    #     print(key)
    #     return key
    # else:return False
#generates the otp if email is provided




#function to handle generating the
class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    def post(self,request, *args, **kwargs):
        # phone = request.data.get('phone')
        # email = request.data.get('email')

        user =request.data
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()#at this point user has been saved
            user_data = serializer.data
            user=User.objects.get(email=user_data['email'])
            #get the user email and send the verification code
            #generate the email otp
            email_otp = EmailOTP(
                otp=get_ottp(),
                owner=user
            )
            email_otp.save()
            #====have to save it to our database======
            #now have to mailthe user with the otp
            email_body = '<## ==== {}, is your Spark Remit verification code. ###>'.format(email_otp.otp)
            data = {
                'email_body':email_body,
                'to_email':user.email ,
                'email_subject':'Spark Remit verification'
            }
            Util.send_email(data)
            return Response({'status':True,'message':'Verification initiated'},
                status=status.HTTP_201_CREATED)
        else:
            return Response({'status':False,'message':'Check details'},
            status=status.HTTP_400_BAD_CONTENT)


#====view to handle resending the otp===
class ResendOTPView(APIView):
    def post(self,request, *args, **kwargs):
        email = request.query_params['email']

        try:
            user_targ = User.objects.get(email=email)
            if user_targ:
                email_otp = EmailOTP(
                    otp=get_ottp(),
                    owner=user_targ
                )
                email_otp.save()
                email_body = '<#===={}, is your new Spark Remit verification code #>'.format(email_otp.otp)
                data = {
                    'email_body':email_body,
                    'to_email':user_targ.email ,
                    'email_subject':'Spark Remit verification'
                }
                Util.send_email(data)
                return Response({'status':True,'message':'Verification code  sent '},status=status.HTTP_201_CREATED)
            else:
                return Response({'status':False,'message':'Register again'})
        except User.DoesNotExist:
            return Response({
                'status':False,
                'message':'User with Email Not Found'
            })





#====view to handle creating admin user ======
class RegisterAdmin(APIView):
    serializer_class = AdminSerializer
    def post(self,request, *args, **kwargs):
        """
            view to handle creating admin user, wat am going to do is i will create it
            then real admin user will just change the password.
        """
        email = request.data.get('email',False)
        username = request.data.get('username',False)
        password = request.data.get('password',False)

        if email and username and password:
            temp_data = {
                'email':email,
                'username':username,
                'password':password
            }
            serializer = AdminSerializer(data=temp_data)
            serializer.is_valid(raise_exception=True)
            admin = serializer.save()
            admin.set_password(password)
            admin.save()
            return Response({
                'status':True,
                'message':'admin created'
            })
        else:
            return Response({
                'status':False,
                'message':'Provide Credentials'
            })


#==========login the admin=========
class AdminLoginView(APIView):
    def post(self,request,*args, **kwargs):
        username = request.query_params['username']
        password = request.query_params['password']

        if username and password:
            try:
                now_admin = UserAdmin.objects.get(username=username)
                if now_admin.password == password:
                    return Response({
                        "status":True,
                        "message":"Admin Login Successful"
                    })
                else:
                    return Response({
                        "status":False,
                        "message":"Admin login Failed"
                    })
            except UserAdmin.DoesNotExist:
                return Response({
                    'status':False,
                    'message':'Admin not Found'
                })
        else:
            return Response({
                'status':False,
                'message':'Provide username and password'
            })


class AdminDetails(APIView):
    def get(self,request,*args, **kwargs):
        admins = UserAdmin.objects.select_related()
        admin_real = admins.first()
        username = admin_real.username
        email = admin_real.email
        password = admin_real.password
        return Response({
            'status':True,
            'username':username,
            'email':email,
            'password':password
        })

#===next step is to validate the otp which was sent in the email
class ValidateOTPView(APIView):
    serializer_class = VerifyUserSerializer
    def post(self, request, *args, **kwargs):
        OTP = request.data["otp"]


        # user_for_email = User.objects.get(email=email)
        # #==finding the email_otp
        try:
            email_otp_reqd = EmailOTP.objects.get(otp=OTP)
            emailotp_owner = email_otp_reqd.owner
            print(emailotp_owner)
            #==verify the use====
            emailotp_owner.is_verified = True
            emailotp_owner.save()
            return Response({
                'status':True,
                'message':'User verified successfully',
                'verified_email':emailotp_owner.email
            })
        #this actually gets the Email otp and we can use it to get the owner

        except EmailOTP.DoesNotExist:
            return Response({
                'status':False,
                'message':'Please check the verification code',

            })

class CreatePinView(APIView):
    serializer_class = CreatePinSerializer
    def post(self,request, *args,**kwargs):
        email = request.data['email']
        PIN = request.data['PIN']

        try:
            user_target = User.objects.get(email=email)
            if len(str(PIN)) == 4:

                if user_target.is_verified:
                    #want to only let verified users create pin
                    user_target.PIN = PIN
                    #====variable to help track pin creation
                    user_target.pin_created = True
                    user_target.save()
                    return Response({
                        'status':True,
                        'message':'PIn created successfully'
                    })
                else:
                    return Response({
                        'status':False,
                        'message':'User was not verified'
                    })
            else:
                return Response({'status':False,'message':'PIN must be 4 xters'})
        except User.DoesNotExist:
            return Response({
                'status':False,
                'message':'User Not Found, Create User'
            })


#===case when user forgot pin==just ue same view
class ForgotPINView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.query_params['email']
        PIN = request.query_params['PIN']

        try:
            user_targ =  User.objects.get(email=email)
            if user_targ and user_targ.is_verified:
                if len(str(PIN)) == 4:
                    user_targ.PIN = int(PIN)
                    user_targ.save()
                    return Response({
                        'status':True,
                        'message':"PIN updated successfully"
                    })
                else:
                    return Response({
                        'status':False,
                        'message':"PIN must be 4 ints"
                    })
            else:
                return Response({
                    'status':False,
                    'message':"Verify email first"
                })
        except User.DoesNotExist:
            return Response({
                'status':False,
                'message':'User Not Found, Create User'
            })







class LoginView(APIView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        PIN = request.query_params['PIN']

        all_users = User.objects.filter(PIN=PIN)
        if len(all_users) == 1 or len(all_users) > 1:
            user_target = all_users[0]
            if len(str(PIN)) == 4:
                if user_target.is_verified:
                    #now check if pin is equal to PIN
                    if user_target.PIN == int(PIN):
                        return Response({
                            'status':True,
                            'email': user_target.email,
                            'message':'PIN match successful'
                        })
                    else:
                        return Response({
                            'status':False,
                            'message':'Wrong PIN Match, Create New PIN'
                        })
                else:
                    return Response({
                        'status':False,
                        'message':'User wasnot verified'
                    })
            else:
                return Response({
                    'status':False,
                    'message':'PIN must be 4 xters'
                })
        else:
            return Response({
                'status':False,
                'message':'User Not Found, Create User'
            })






#====now this is for adding a username=======
class AddUsernameView(APIView):
    serializer_class = CreateUserNameSerializer
    def post(self,request, *args, **kwargs):
        email = request.data['email']
        uname = request.data['uname']

        if email and uname:
            try:
                user_target = User.objects.get(email=email)
                if uname[0] == '@':
                    uname = uname
                else: uname = '@'+uname
                #since we want the username to be @
                #add username to the user
                #==first check if the username is available
                check_if_user = User.objects.filter(uname=uname)
                if check_if_user.exists():
                    return Response({
                        'status':False,
                        'message':'Username not available'
                    })
                else:
                    user_target.uname = uname
                    user_target.save()
                    #===== saving the uname to the database====
                    return Response({
                        'status':True,
                        'message':'Username added'
                    })
            except User.DoesNotExist:
                return Response({
                    'status':False,
                    'message':'User Not Found, Create User'
                })
        else:
            return Response({
                'status':False,
                'message':'Provide uname and email'
            })






#=====view to list total number of users registered, registered permonth,
class UserAnalyticsView(APIView):
    def get(request, *args, **kwargs):
        """
            but wait how do i verify that the request is from the admin
            ==
            task is to get the total users registered, registered per month, registered by country
        """
        #total_users = User.objects.select_related()#just want to use select_related to be modify my queries
        #but remmember this returns a query, use aggregate to get sum
        # total_number_users = [s
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        #supported countries
        countries = ["Uganda","Kenya","Tanzania","Rwanda","Burundi","UAE","Nigeria"]
        total_users = User.objects.count()#this gives me total users

        all_users =  User.objects.select_related()

        # month_count_dict = {month:count for month in months for count in  all_users.User.objects.filter(get_month=month).count()}
        #awesome this now gives me the dictionary i need

        # total_country_users = {country:user.count for country in countries for count in User.objects.filter(country=country).count()}

        #====now i need to get the
        #=======should also work on the
        #===getting the total amount for topup and for withdraw
        #======
        countrys = [user.country for user in all_users]
        count = [user.country.count(user.country) for user in all_users]
        total_country_users = dict(Counter([user.country for user in all_users]))


        # top_ups = Payment.objects.filter(status='COMPLETE',category='TOP_UP').aggregate(Sum('amount'))
        total_top = [int(user.amount) for user in Payment.objects.filter(status='COMPLETE',category='TOP_UP')]
        total_top = sum(total_top)
        # withdraws = Payment.objects.filter(status='COMPLETE',category='WITHDRAW').aggregate(total_with = Sum('amount'))
        total_with = [int(user.amount) for user in Payment.objects.filter(status='COMPLETE',category='WITHDRAW')]
        total_with  = sum(total_with)

        #=====last is the profits to be made======
        #====first get calculate the withdraws ==========
        # total_profits = Profits.objects.select_related().aggregate(Sum('profit_amount'))
        total_profit = [int(user.profit_amount) for user in Profits.objects.select_related()]
        total_profit = sum(total_profit)


        return Response({
            'status':True,
            'total_users':total_users,
            'total_topup':total_top,
            'total_withdraw':total_with,
            'total_profit':total_profit,
            'countries':countrys,
            'count':count,
            'message':'user analytics returned'
        })















