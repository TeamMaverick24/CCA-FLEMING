from typing import Iterable
from django.db import models
from dh_user.models import Student
from django.utils import timezone
from django.conf import settings
# Create your models here.


class GamesType(models.Model):
    tittle = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(default='')
    status = models.BooleanField(default=1)

    def __str__(self):
        return self.tittle

class GamesOptions(models.Model):
    tittle = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(default='')
    status = models.BooleanField(default=1)

GAME_MODE = (
        ('options', 'Options'),
        ('qr', 'QR Code'),
        ('image', 'Image Upload'),
    )

class Games(models.Model):
    tittle = models.CharField(max_length=100, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    description = models.TextField(default='')
    status = models.BooleanField(default=1)
    options = models.ManyToManyField(GamesOptions, blank=True)
    game_type = models.ForeignKey(GamesType, on_delete=models.CASCADE, blank=True, null=True)
    qr_code = models.FileField(upload_to="qrcode", blank=True, null=True,default='')
    answer_value = models.CharField(max_length=250, blank=True, null=True)
    mode = models.CharField(max_length=50, default="qr",choices=GAME_MODE)
    collage_name = models.CharField(max_length=100, null=True)

    def save(self, *args, **kwargs):
        self.qr_generator(self, *args, **kwargs)
        return super().save(*args, **kwargs)

    def qr_generator(self, *args, **kwargs):
        try:

            if self.mode != "qr":
                return True
            
            if self.answer_value:
                return True
            
            import string
            import random
            import qrcode
            import os

            img_dir = os.path.join(settings.MEDIA_ROOT, 'qrcode')
            os.makedirs(img_dir, exist_ok=True) 
            
            unic_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
            unic_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
            
            img = qrcode.make(unic_code)

            img_name = f'{unic_name}.png'
            img_path = os.path.join(img_dir, img_name)
            img.save(img_path)

            self.qr_code = os.path.relpath(img_path, settings.MEDIA_ROOT)
            self.answer_value = unic_code
            self.save()


        except Exception as e:
            import traceback
            traceback.print_exc()

    
    def __str__(self):
        return self.tittle


STATUS = (
        ('C', 'Completed'),
        ('O', 'Open'),
        ('F', 'Failed'),
        ('P', 'Pending'),
    )

class GameUser(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    notes = models.TextField(default='')
    answer_value = models.TextField(default='')
    status = models.CharField(max_length=50, null=True,choices=STATUS)

class UserUpload(models.Model):
    # profile = models.ForeignKey(GameUser, on_delete=models.CASCADE,null=False,blank=True)
    picture = models.FileField(upload_to="user-uploads", null=False,default='')
    created  = models.DateTimeField(default=timezone.now)


class GamesScoreBoard(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    game_level = models.ForeignKey(GamesType, on_delete=models.CASCADE, blank=True, null=True)
    total_games = models.CharField(max_length=250, blank=True, null=True)
    success_games = models.CharField(max_length=250, blank=True, null=True)
    played_games = models.CharField(max_length=250, blank=True, null=True)
    update = models.DateTimeField(auto_now=True)
    # played_ids = JSONField(default=list)

