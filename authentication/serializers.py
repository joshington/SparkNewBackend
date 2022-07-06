#from dataclasses import fields
from rest_framework import serializers
from .models import EmailOTP, User,UserAdmin

from django.contrib.auth import authenticate

#registering the new user
#==since the flow has chnaged somehow
class RegisterSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(max_length=68, min_length=6,write_only=True)
    class Meta:
        model = User
        fields=['phone','email','country']

    #hashing the password
    def create(self, validated_data):
        email = validated_data['email']
        phone = validated_data['phone']
        country = validated_data['country']
        if email and phone and country:
            instance = self.Meta.model(**validated_data)
        instance.save()
        return instance
        # password = validated_data.pop('password', None)
        # instance = self.Meta.model(**validated_data)
        # if password is not None:
        #     instance.set_password(password)
        # instance.save()
        # return instance

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAdmin
        fields = ['email','username','password']
        extra_kwargs = {'password':{'write_only':True}}

        def create(self, validated_data):
            user = UserAdmin.objects.create(**validated_data)
            return user




class AdminLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAdmin
        fields = ['username','password']


class VerifyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailOTP
        fields = ['otp']

class CreatePinSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','PIN']

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','PIN']

class CreateUserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','uname']

    # def validate(self,attrs):
    #     #take username and password requet
    #     email = attrs.get('email')
    #     password = attrs.get('password')

    #     if email and password:
    #         user = authenticate(request=self.context.get('request'),
    #                             email=email, password=password)
    #         if not user:
    #             # If we don't have a regular user, raise a ValidationError
    #             msg = 'Access denied: wrong username or password.'
    #             raise serializers.ValidationError(msg, code='authorization')
    #     else:
    #         msg = 'Both "username" and "password" are required.'
    #         raise serializers.ValidationError(msg, code='authorization')
    #     attrs['user'] = user
    #     return attrs