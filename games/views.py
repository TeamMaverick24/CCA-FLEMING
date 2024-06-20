from rest_framework import viewsets, status
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from games.models import *
from .serializer import *
# Create your views here.


class GamesTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Games level type for example : Game Level 1, Game Level 2, Game Level 3.
    """
    permission_classes = [IsAuthenticated]
    queryset = GamesType.objects.all()
    serializer_class = GamesTypeSerializer
    http_method_names = ['get', 'post', 'put']


class GamesOptionsViewSet(viewsets.ModelViewSet):
    """
    An API endpoint that allows Games Options to answer with one of the options. 
    """
    permission_classes = [IsAuthenticated]
    queryset = GamesOptions.objects.all()
    serializer_class = GamesOptionsSerializer
    http_method_names = ['get', 'post', 'put']


class GamesViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows to \n
        Create new Game from admin side \n. 
        Update Existing Game from admin side \n. 
        List games and their statuses on the user interface, showing locked and unlocked games \n.
    """
    permission_classes = [IsAuthenticated]
    queryset = Games.objects.all()
    serializer_class = CreateGameSerializer
    http_method_names = ['get', 'post', 'put']

    # def create(self, request, *args, **kwargs):
    #     try:
    #         post_data = request.post


    #         return Response({'data': {}}, status=status.HTTP_200_OK)
        
    #     except:
    #         return Response({'error': "No post found"}, status=status.HTTP_404_NOT_FOUND)

class GetUserGameList(APIView):
    serializer_class = GameSerializer
    """
        API endpoint that shows all games in 

    """
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            game_type = request.GET.get('game_type')
            game_list = []
            user_start_games = GameUser.objects.filter(user=request.user,game__game_type__id=game_type).all().order_by('game__level')
            last_level = 0
            for game_ob in user_start_games:
                game_list.append({
                    "id":game_ob.game.pk,
                    "tittle":game_ob.game.tittle,
                    "description":game_ob.game.description,
                    "status":game_ob.status,
                })
                last_level = game_ob.game.level
            
            game_objs = Games.objects.filter(level__gt=last_level,game_type__id=game_type).all()
            for game_obj in game_objs:
                game_list.append({
                    "id":game_obj.pk,
                    "tittle":game_obj.tittle,
                    "description":game_obj.description,
                    "status":"",
                }) 
            
            return Response({'data': game_list}, status=status.HTTP_200_OK)
        except:
            return Response({'error': "No post found"}, status=status.HTTP_404_NOT_FOUND)


class GameLevelUpdate(APIView):
    # authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    serializer_class = GameSerializer
    def get(self, request, *args, **kwargs):
        try:
            game_id = request.GET.get('game_id')
            game_obj = Games.objects.filter(id=game_id).values().first()

            return Response({'message': "Game Details.",'data':game_obj}, status=status.HTTP_200_OK)
        except:
            return Response({'error': "No data found"}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, *args, **kwargs):
        try:
            game_id = request.data['game_id']
            game_status = request.data['status']
            game_notes = request.data['notes']
            user = request.user
            game_obj = Games.objects.filter(id=game_id).first()
            user_game = GameUser.objects.filter(user=user,game=game_obj).first()
            if user_game:
                user_game.notes = game_notes
                user_game.status = game_status
                user_game.save()
            else:
                GameUser.objects.create(
                    user=user,
                    game=game_obj,
                    notes=game_notes,
                    status=game_status,
                )

            return Response({'message': "level updated."}, status=status.HTTP_200_OK)
        except:
            return Response({'error': "No post found"}, status=status.HTTP_404_NOT_FOUND)