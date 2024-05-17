from rest_framework import serializers
from rest_framework import viewsets, status
from email.policy import default
from rest_framework import serializers
from rest_framework import viewsets, status
from .models import *
from django_countries.serializers import CountryFieldMixin


class GamesTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamesType
        fields = "__all__"


class GamesOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamesOptions
        fields = "__all__"

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Games
        fields = "__all__"


class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Games
        fields = "__all__"

