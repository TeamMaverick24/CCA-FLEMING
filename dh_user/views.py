from rest_framework import viewsets, status,generics
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
    http_method_names = ['get', 'post', 'put','delete']

    def get_queryset(self):
        campus_name = self.request.GET.get('campus_name', None)
        if campus_name:
            self.queryset = self.queryset.filter(collage_name=campus_name)
        
        active_student = self.request.GET.get('active_student', None)
        if active_student:
            self.queryset = self.queryset.filter(is_deleted=False)

        return self.queryset
    
    def get_permissions(self):

        if self.action == 'create':
            permission_classes = []
        elif self.action == 'otp_verification':
            permission_classes = []
        elif self.action == 'user_login':
            permission_classes = []
        elif self.action == 'reset_password':
            permission_classes = [IsAdminOrIsSelf]
        elif self.action == 'admin_user_create':
            permission_classes = [IsAdminOrIsSelf]
        elif self.action == 'forgot_password':
            permission_classes = []
        elif self.action == 'otp_reset_password':
            permission_classes = []
        elif self.action == 'delete':
            permission_classes = []
        elif self.action == 'update':
            permission_classes = [IsAdminOrIsSelf]
        elif self.action == 'delete_all':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = []
        
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):

            if self.action == 'create':
                return CreateUserSerializer
            elif self.action == 'admin_user_create':
                return CreateUserSerializer
            elif self.action == 'otp_verification':
                return UserOtpSerializer
            elif self.action == 'user_login':
                return UserLoginSerializer
            elif self.action == 'update':
                return UpdateUserSerializer
            elif self.action == 'delete':
                return UpdateUserSerializer
            elif self.action == 'reset_password':
                return ResetPasswordSerializer
            elif self.action == 'otp_reset_password':
                return ForgotPasswordSerializer
            elif self.action == 'forgot_password':
                return ForgotPasswordSerializer
            elif self.action == 'delete_all':
                return UserOtpSerializer
            else:
                return UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            headers = {}
            request_data = request.data
            request_data['is_active'] = False
            request_data['is_staff'] = False
            request_data['is_admin'] = False
            email = request_data['email']
            otp = self.generate_otp()
            request_data['email_otp'] = otp

            student_obj = Student.objects.filter(email=email,is_active=False).first()
            if not student_obj:
                serializer = self.get_serializer(data=request_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
            else:
                student_obj.email_otp = otp
                student_obj.save()
            
            self.send_otp_email(email, otp)

            res = {
                "message": "Details Successfully created",
                "status": "success",
                "response_code": status.HTTP_200_OK
            }
            
            return Response(res, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            import traceback
            traceback.print_exc()
            message = str(e)
            return Response({'status':'error','response_code':500,"message":message})
    
    @action(methods=['post'], detail=False, url_path='admin-user-create')
    def admin_user_create(self, request, *args, **kwargs):
        try:
            headers = {}
            request_data = request.data
            email = request_data['email']

            student_obj = Student.objects.filter(email=email,is_active=False).first()
            if not student_obj:
                student_obj = Student()
                student_obj.is_active = True
                student_obj.is_staff = True
                student_obj.is_superuser = True
                student_obj.email = email
                student_obj.contact_number = request_data['contact_number'] if 'contact_number' in request_data else ""
                student_obj.collage_name = request_data['collage_name']
                student_obj.username = request_data['username']
                student_obj.set_password(request_data['password'])
                student_obj.save()
                res = {
                    "message": "Admin User Created Successfully",
                    "status": "success",
                    "response_code": status.HTTP_200_OK
                }
            else:
                res = {
                    "message": "Email Address Already Registred.",
                    "status": "failed",
                    "response_code": status.HTTP_400_BAD_REQUEST
                }
            
            return Response(res, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            import traceback
            traceback.print_exc()
            message = str(e)
            return Response({'status':'error','response_code':500,"message":message})

    @action(methods=['post'], detail=False, url_path='otp-verification')
    def otp_verification(self, request, *args, **kwargs):
        try:
            request_data = request.data
            email = request_data['email']
            mail_otp = request_data['mail_otp']
            student_obj = Student.objects.filter(email=email,is_active=False,email_otp=mail_otp).first()
            if student_obj:
                student_obj.is_active = True
                student_obj.save()
                return Response({'status': True,"message":"Mail verified successfully."})
            else:
                return Response({'status': False,"message":"Mail not verified."})
            
        except Exception as e:
            message = str(e)
            return Response({'status':message,'response_code':500,"message":message})
    
    @action(methods=['post'], detail=True, url_path='reset-password')
    def reset_password(self, request, *args, **kwargs):
        password = request.data.pop('password')
        user = self.get_object()
        user.set_password(password)
        user.save()
        return Response({'status': True})
    
    @action(methods=['post'], detail=False, url_path='forgot-password')
    def forgot_password(self, request, *args, **kwargs):
        email = request.data.pop('email')
        if not email:
            return Response({'status': False,"message":"Please enter your email address."})
        
        otp = self.generate_otp()
        self.send_otp_email(email, otp)

        return Response({'status': True,"message":"OTP Send Successfully"})

    @action(methods=['get'], detail=False, url_path='delete-all')
    def delete_all(self, request, *args, **kwargs):

        Student.objects.filter(is_staff=False,is_superuser=False).delete()
        return Response({'status': True,"message":"Users Deleted Successfully"})
    
    def send_otp_email(self,to_email, otp):
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        student_obj = Student.objects.filter(email=to_email).first()

        subject = 'Your OTP Code'
        message = render_to_string('otp_email.html', {'otp': otp})
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [to_email]
        student_obj.email_otp = otp
        student_obj.save()

        send_mail(subject, '', email_from, recipient_list, html_message=message)

    def generate_otp(self):
        import random
        return random.randint(100000, 999999)

    @action(methods=['post'], detail=False, url_path='otp-reset-password')
    def otp_reset_password(self, request, *args, **kwargs):
        password = request.data.pop('password')
        email = request.data.pop('email')
        otp = request.data.pop('otp')
        student_obj = Student.objects.filter(email=email).first()
        if otp == student_obj.email_otp:
            student_obj.set_password(password)
            student_obj.save()
            return Response({'status': True,"message":"Password update Successfully"})
        else:
            return Response({'status': False,"message":"Password not updated."})
    

    @action(methods=['post'], detail=False, url_path='user-login')
    def user_login(self, request, *args, **kwargs):
        username = request.data.get("email")
        password = request.data.get("password")
        try:
            student_obj = Student.objects.get(email=username)
            if student_obj and check_password(password,student_obj.password):
                game_data = {}
                from games.models import GameUser
                game_obj = GameUser.objects.filter().select_related('game').last()
                if game_obj:
                    game_data["curent_level"] = game_obj.game.game_type.tittle
                    game_data["curent_game"] = game_obj.game.tittle

                refresh = RefreshToken.for_user(student_obj)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'status': True,
                    'name': student_obj.username,
                    'contact_number': student_obj.contact_number,
                    'is_staff': student_obj.is_staff,
                    "collage_name":student_obj.collage_name,
                    **game_data
                })

        except:
            return Response({'message':"Email address not found.",'status': False})

        return Response({'message':"Invalid credentials.",'status': False})
    
    @action(methods=['delete'], detail=True, url_path='delete')
    def delete(self, request, *args, **kwargs):
        Student.objects.filter(id=kwargs["pk"]).delete()
        return Response({'message':"User Delete Successfull.",'status': True})
    
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    
    


class UserList(generics.ListAPIView):
    queryset = Student.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        


        response_data = super().get(self, request, *args, **kwargs)
        return Response({'message':"Student List.",'status': True,"data":response_data.data})