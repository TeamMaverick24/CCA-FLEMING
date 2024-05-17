from rest_framework import viewsets, status
from .models import Student
from email.policy import default
from rest_framework import permissions

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from dh_user.permissions import IsUserAddressOwner, IsUserProfileOwner

from dh_user.mail import send_verify_email
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
        elif self.action == 'reset_password':
            permission_classes = [IsAdminOrIsSelf]
        elif self.action == 'send_verify_email':
            permission_classes = [IsAdminOrIsSelf]
        elif self.action == 'verify_email':
            permission_classes = []
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
            elif self.action == 'reset_password':
                return ResetPasswordSerializer
            elif self.action == 'verify_email':
                return None
            elif self.action == 'send_verify_email':
                return None
            else:
                return UserSerializer


    @action(methods=['post'], detail=False, url_path='user-login')
    def user_login(self, request, *args, **kwargs):
        username = request.data.get("email")
        password = request.data.get("password")
        try:
            student_obj = Student.objects.get(email=username)
            if student_obj and check_password(password,student_obj.password):
                refresh = RefreshToken.for_user(student_obj)
                return Response({'refresh': str(refresh),'access': str(refresh.access_token),'status': True})
        except:
            return Response({'message':"Email address not found.",'status': False})

        return Response({'message':"Invalid credentials.",'status': False})
    
    @action(methods=['post'], detail=True, url_path='reset-password')
    def reset_password(self, request, *args, **kwargs):
        password = request.data.pop('password')
        user = self.get_object()
        user.set_password(password)
        user.save()
        return Response({'status': True})

    
    @action(methods=['post'], detail=False, url_path='send-verify-email')
    def send_verify_email(self, request):
        user = request.user
        user.email_code = BaseUserManager().make_random_password(length=50)
        user.save()
        link = settings.SERVER_HOST + '/api/user/' + f'{user.id}/verify-email/?email_code={user.email_code}'
        send_verify_email(request.user, link)
        return Response({'msg': f'Verification Email has been sent to {user.email}'})

    
    @action(methods=['get'], detail=True, url_path='verify-email')
    def verify_email(self, request, pk):
        user = self.get_object()
        code = request.GET.get('email_code')
        if (user.email_code != code):
            return Response({'error': 'Invalid Verified Code'}, status=status.HTTP_400_BAD_REQUEST)
        user.email_verified = True
        user.email_code = None
        user.save()
        return HttpResponseRedirect(redirect_to=settings.WEB_HOST)


    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    
    


