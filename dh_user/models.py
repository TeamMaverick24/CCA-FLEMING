from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_countries.fields import CountryField
import logging


class SOCIAL_AUTH_PLATFORM(models.TextChoices):
    NONE = 'NONE', _('NONE')
    GOOGLE = 'GOOGLE', _('GOOGLE')

class FILE_TYPES(models.TextChoices):
    NONE = 'NONE', _('NONE')
    IMAGE = 'IMAGE', _('IMAGE')
    PDF = 'PDF', _('PDF')
    DOC = 'DOC', _('DOC')
    VIDEO = 'VIDEO', _('VIDEO')


class StudentManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
            Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # user.is_admin = True
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        
        return self.create_user(email, password, **extra_fields)


class Student(AbstractBaseUser,PermissionsMixin):
    class Meta:
        db_table = 'Student'

    objects = StudentManager()

    username = None
    USERNAME_FIELD = 'email'
    
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    
    date_joined = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False) # Super Admin User
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=100,null=True)
    contact_number = models.CharField(max_length=100, null=True)
    email_code = models.CharField(max_length=100, null=True)
    collage_name = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, null=True)
    
    REQUIRED_FIELDS = ['username','contact_number']

    def __str__(self):
        return f"{self.username} {self.email}"

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_admin(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin




