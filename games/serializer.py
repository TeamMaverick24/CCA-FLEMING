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
    game_options = serializers.SerializerMethodField('get_options')
    class Meta:
        model = Games
        fields = "__all__"
    
    def get_options(self, obj):
        options_value = []
        if obj.mode and obj.mode == "options" and obj.options:
            options_value = list(obj.options.values('id','tittle','description').all())
        
        return options_value



class CreateGameSerializer(serializers.ModelSerializer): 
    game_options = serializers.SerializerMethodField('get_options')
    class Meta:
        model = Games
        fields = "__all__"

    def get_options(self, obj):
        options_value = []
        if obj.mode and obj.mode == "options" and obj.options:
            options_value = list(obj.options.values('id','tittle','description').all())
        
        return options_value

class UserUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUpload
        fields = ('picture',)


class GameUserSerializer(serializers.ModelSerializer):
    game_user = serializers.SerializerMethodField('get_game_user')
    game_value = serializers.SerializerMethodField('get_game_value')
    class Meta:
        model = GameUser
        fields = "__all__"
    
    def get_game_user(self, obj):
        options_value = {}
        if obj.user:
            options_value["username"] = obj.user.username
            options_value["collage_name"] = obj.user.collage_name
            options_value["email"] = obj.user.email
            # options_value = dict(obj.user.values().first())
        return options_value

    def get_game_value(self, obj):
        options_value = {}
        if obj.game:
            options_value["tittle"] = obj.game.tittle
            options_value["description"] = obj.game.description
            options_value["qr_code"] = obj.game.qr_code.url if obj.game.qr_code else ""
            options_value["answer_value"] = obj.game.answer_value
            options_value["mode"] = obj.game.mode
        return options_value
    

class GamesScoreBoardSerializer(serializers.ModelSerializer): 
    class Meta:
        model = GamesScoreBoard
        fields = "__all__"