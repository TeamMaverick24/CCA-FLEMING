from django.db import models
from dh_user.models import Student
# Create your models here.


class GamesType(models.Model):
    tittle = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(default='')
    status = models.BooleanField(default=1)

class GamesOptions(models.Model):
    tittle = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(default='')
    status = models.BooleanField(default=1)

class Games(models.Model):
    tittle = models.CharField(max_length=100, blank=True, null=True)
    level = models.IntegerField(unique=True)
    description = models.TextField(default='')
    status = models.BooleanField(default=1)
    options = models.ManyToManyField(GamesOptions, blank=True)
    game_type = models.ForeignKey(GamesType, on_delete=models.CASCADE, blank=True, null=True)


STATUS = (
        ('C', 'Completed'),
        ('O', 'Open'),
        ('F', 'Failed'),
    )

class GameUser(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    notes = models.TextField(default='')
    status = models.CharField(max_length=50, null=True,choices=STATUS)

