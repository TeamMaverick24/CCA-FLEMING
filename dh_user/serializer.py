from rest_framework import serializers
from rest_framework import viewsets, status
from .models import Student
from email.policy import default
from rest_framework import serializers
from rest_framework import viewsets, status
from .models import *
from django_countries.serializers import CountryFieldMixin


class UserOtpSerializer(serializers.ModelSerializer):
    mail_otp = serializers.IntegerField() 
    class Meta:
        model = Student
        fields = ['mail_otp', 'email']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['password', 'email_code','is_staff','groups','user_permissions']

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['password', 'email']

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['password','is_active', 'email_verified', 'email_code','groups','user_permissions']
    
    def to_representation(self, instance):
        return UserSerializer(instance=instance).data

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['email_code','groups','user_permissions']
        extra_kwargs = {'is_staff': {'read_only': True},'is_admin': {'read_only': True}, 'is_active': {'read_only': True}, 'last_login': {'read_only': True}, 'email_verified': {'read_only': True}, 'password': {'write_only': True},}

    def validate(self, data):
        email = data['email']
        password = data['password']
        SpecialSym = ['$','@','#','%']


        if len(password) < 6 :
            raise serializers.ValidationError("Password length should be at least 6")
        
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError('Password should have at least one numeral')
            
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError('Password should have at least one uppercase letter')
            
        if not any(char.islower() for char in password):
            raise serializers.ValidationError('Password should have at least one lowercase letter')

        if not any(char in SpecialSym for char in password):
            raise serializers.ValidationError('Password should have at least one lowercase letter')
        
        email_split = email.split("@")
        if email_split[1] != "flemingcollege.ca" :
            raise serializers.ValidationError("Please enter a registered Fleming email")
            
        return super().validate(data)
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Student(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        return UserSerializer(instance=instance).data

class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['password']


class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['email']