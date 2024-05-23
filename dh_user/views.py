from rest_framework import viewsets, status
from .models import Student
from email.policy import default
from rest_framework import permissions

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from dh_user.permissions import IsUserAddressOwner, IsUserProfileOwner

from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password

import logging

from .serializer import *


class IsAdminOrIsSelf(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id or request.user.is_admin


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Student.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'put']
    
    def get_permissions(self):

        if self.action == 'create':
            permission_classes = []
        elif self.action == 'user_login':
            permission_classes = []
        elif self.action == 'delete':
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'update':
            permission_classes = [IsAdminOrIsSelf]
        else:
            permission_classes = []
        
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):

            if self.action == 'create':
                return CreateUserSerializer
            elif self.action == 'user_login':
                return UserLoginSerializer
            elif self.action == 'update':
                return UpdateUserSerializer
            else:
                return UserSerializer


    @action(methods=['post'], detail=False, url_path='user-login')
    def user_login(self, request, *args, **kwargs):
        username = request.data.get("email")
        password = request.data.get("password")
        try:
            student_obj = Student.objects.get(email=username)
            if student_obj and check_password(password,student_obj.password):
                print(student_obj.__dict__)
                refresh = RefreshToken.for_user(student_obj)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'status': True,
                    'name': student_obj.username,
                    'contact_number': student_obj.contact_number,
                    'is_staff': student_obj.is_staff,
                })

        except:
            # import traceback
            # traceback.print_exc()
            return Response({'message':"Email address not found.",'status': False})

        return Response({'message':"Invalid credentials.",'status': False})
    

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    
    


