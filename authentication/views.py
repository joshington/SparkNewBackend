from django.shortcuts import render
from rest_framework import generics, status,views
from rest_framework.views import APIView
from rest_framework import serializers
# Create your views here.
from rest_framework.response import Response 
from .serializers import*
from .models import*

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
            email_body = '{}, is your Spark Remit verification code'.format(email_otp.otp)
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

class LoginView(APIView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        email = request.data['email']
        PIN = request.data['PIN']

        try:
            user_target = User.objects.get(email=email)
            if len(str(PIN)) == 4:
                if user_target.is_verified:
                    #now check if pin is equal to PIN
                    if user_target.PIN == PIN:
                        return Response({
                            'status':True,
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
        except User.DoesNotExist:
            return Response({
                'status':False,
                'message':'User Not Found, Create User'
            })
                    

#====now this is for adding a username=======
class AddUsernameView(APIView):
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


            

        


       

    
           


       
            


           