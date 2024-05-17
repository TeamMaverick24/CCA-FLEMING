from rest_framework import serializers
from rest_framework import viewsets, status
from .models import Student
from email.policy import default
from rest_framework import serializers
from rest_framework import viewsets, status
from .models import *
from django_countries.serializers import CountryFieldMixin

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['password', 'email_code','is_staff']

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['password', 'email']

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['password','is_active', 'email_verified', 'email_code']
    
    def to_representation(self, instance):
        return UserSerializer(instance=instance).data

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['email_code']
        extra_kwargs = {'is_staff': {'read_only': True},'is_admin': {'read_only': True}, 'is_active': {'read_only': True}, 'last_login': {'read_only': True}, 'email_verified': {'read_only': True}, 'password': {'write_only': True},}

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

