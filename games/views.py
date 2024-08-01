from rest_framework import viewsets, status,generics
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from dh_user.permissions import IsActiveStudent
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from django.db.models import Q

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


class GamesViewSetModel(viewsets.ModelViewSet):
    """
        API endpoint that allows to \n
        Create new Game from admin side \n. 
        Update Existing Game from admin side \n. 
        List games and their statuses on the user interface, showing locked and unlocked games \n.
    """
    permission_classes = [IsAuthenticated]
    queryset = Games.objects.all()
    serializer_class = CreateGameSerializer
    http_method_names = ['get', 'post','put','delete']

    def get_queryset(self):
        game_type = self.request.GET.get('game_type', None)
        if game_type:
            self.queryset = self.queryset.filter(game_type__id=game_type)
        
        game_mode = self.request.GET.get('game_mode', None)
        if game_mode:
            self.queryset = self.queryset.filter(mode=game_mode)

        collage_name = self.request.GET.get('campus_name', None)
        if collage_name:
            self.queryset = self.queryset.filter(collage_name=collage_name)

        return self.queryset

    def create(self, request):
        post_data = request.data
        game_tittle = str(post_data["tittle"])
        game_tittle = game_tittle.title()

        if Games.objects.filter(tittle=game_tittle,collage_name=post_data["collage_name"],mode = post_data["mode"]).exists():
            return Response({'message': "Game tittle already exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        #Set your serializer
        game_type_str = "Level " + str(post_data["game_type"])

        game_type = GamesType.objects.filter(Q(tittle=post_data["game_type"]) | Q(tittle=game_type_str)).first()
        if not game_type:
            return Response({'message': "Game type not configured properly."}, status=status.HTTP_400_BAD_REQUEST)
        
        request.data["tittle"] = game_tittle
        request.data["tittle"] = game_type.pk
        serializer = CreateGameSerializer(data=request.data)
        if serializer.is_valid(): #MAGIC HAPPENS HERE
            #... Here you do the routine you do when the data is valid
            #You can use the serializer as an object of you Assets Model
            #Save it
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GamesViewSet(APIView):
    """
        API endpoint that allows to \n
        Create new Game from admin side \n. 
        Update Existing Game from admin side \n. 
        List games and their statuses on the user interface, showing locked and unlocked games \n.
    """
    permission_classes = [IsAuthenticated]
    queryset = Games.objects.all()
    serializer_class = CreateGameSerializer
    # http_method_names = ['get', 'post', 'put']

    def post(self, request, *args, **kwargs):
        try:
            post_data = request.data

            game_tittle = str(post_data["tittle"])
            game_tittle = game_tittle.title()

            if Games.objects.filter(tittle=game_tittle,collage_name=post_data["collage_name"],mode = post_data["mode"]).exists():
                return Response({'message': "Game tittle already exist."}, status=status.HTTP_400_BAD_REQUEST)

            if Games.objects.filter(tittle=post_data["description"],collage_name=post_data["collage_name"],mode = post_data["mode"]).exists():
                return Response({'message': "Game tittle already exist."}, status=status.HTTP_400_BAD_REQUEST)

            #Set your serializer
            game_type_str = "Level " + str(post_data["game_type"])
            game_type = GamesType.objects.filter(Q(tittle=post_data["game_type"]) | Q(tittle=game_type_str)).first()
            options = post_data['options']
            game_code = Games.objects.filter(level=post_data["level"]).count()
            gm = Games()
            gm.tittle = game_tittle
            gm.level = game_code + 1
            gm.description = post_data["description"]
            gm.mode = post_data["mode"]
            gm.collage_name = post_data["collage_name"]
            gm.game_type = game_type

            if "answer_value" in post_data and post_data["answer_value"]:
                answer_value = str(post_data["answer_value"])
                gm.answer_value = answer_value.lower()
            
            gm.save()
            
            if options:
                for op in options:
                    gp = GamesOptions.objects.create(tittle=op,description=op)
                    gm.options.add(gp)
            gm.save()
            respose_data = {
                'message': "Sucessfully created",
                'id': gm.pk,
            }
            if gm.qr_code:
               respose_data.update({"qr_code":settings.SITE_HOST + gm.qr_code.url}) 

            return Response(respose_data, status=status.HTTP_200_OK)

        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_404_NOT_FOUND)

class GetUserGameList(APIView):
    serializer_class = GameSerializer
    """
        API endpoint that shows all games in 
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            game_type = request.GET.get('game_type', None)
            game_mode = request.GET.get('game_mode', None)
            collage_name = self.request.GET.get('campus_name', None)
            game_list = []
            
            user_start_games = GameUser.objects.filter(user=request.user,game__mode=game_mode)
            if game_type:
                user_start_games = user_start_games.filter(game__game_type__id=game_type)
            
            if collage_name:
                user_start_games = user_start_games.filter(game__collage_name=collage_name)
            
            user_start_games = user_start_games.all().order_by('game__level')

            game_ids = []
            for game_ob in user_start_games:
                game_list.append({
                    "id":game_ob.game.pk,
                    "tittle":game_ob.game.tittle,
                    "description":game_ob.game.description,
                    "game_mode":game_ob.game.mode,
                    "status":game_ob.status,
                    "answer_value":game_ob.answer_value,
                })
                game_ids.append(game_ob.game.pk)
            
            game_objs = Games.objects.filter(mode=game_mode).exclude(id__in=game_ids)

            if game_type:
                game_objs = game_objs.filter(game_type__id=game_type)
            
            if collage_name:
                game_objs = game_objs.filter(collage_name=collage_name)

            game_objs = game_objs.all()

            for game_obj in game_objs:
                game_list.append({
                    "id":game_obj.pk,
                    "tittle":game_obj.tittle,
                    "description":game_obj.description,
                    "game_mode":game_obj.mode,
                    "status":"",
                }) 
            
            return Response({'data': game_list}, status=status.HTTP_200_OK)
        except:
            import traceback 
            traceback.print_exc()
            return Response({'error': "No post found"}, status=status.HTTP_404_NOT_FOUND)

class GetUserGameListNew(APIView):
    serializer_class = GameSerializer
    """
        API endpoint that shows all games in 
    """
    permission_classes = [IsAuthenticated]
    def get(self, request,game_level, *args, **kwargs):
        try:
            game_type = request.GET.get('game_type', None)
            game_mode = request.GET.get('game_mode', None)
            collage_name = self.request.GET.get('campus_name', None)
            game_status = self.request.GET.get('game_status', None)
            game_list = []
            
            user_start_games = GameUser.objects.filter(user=request.user,game__mode=game_mode,game__game_type__id=game_level)
            if game_type:
                user_start_games = user_start_games.filter(game__game_type__id=game_type)
            
            if collage_name:
                user_start_games = user_start_games.filter(game__collage_name=collage_name)
            
            if game_status:
                user_start_games = user_start_games.filter(game__status=game_status)
            
            user_start_games = user_start_games.all().order_by('game__level')

            game_ids = []
            for game_ob in user_start_games:
                game_list.append({
                    "id":game_ob.game.pk,
                    "tittle":game_ob.game.tittle,
                    "description":game_ob.game.description,
                    "game_mode":game_ob.game.mode,
                    "status":game_ob.status,
                    "answer_value":game_ob.answer_value,
                })
                last_level = game_ob.game.level
                game_ids.append(game_ob.game.pk)
            
            game_objs = Games.objects.filter(mode=game_mode,game_type__id=game_level)

            if game_ids:
                game_objs = game_objs.exclude(id__in=game_ids)

            if game_type:
                game_objs = game_objs.filter(game_type__id=game_type)
            
            if collage_name:
                game_objs = game_objs.filter(collage_name=collage_name)
            
            if game_status:
                game_objs = game_objs.filter(status=game_status)

            game_objs = game_objs.all().order_by('level')
            status_value = "O"
            for game_obj in game_objs:
                game_list.append({
                    "id":game_obj.pk,
                    "tittle":game_obj.tittle,
                    "description":game_obj.description,
                    "game_mode":game_obj.mode,
                    "status":status_value,
                    "qr_code":game_obj.qr_code.url if game_obj.qr_code else "",
                    "options":list(game_obj.options.values('id','tittle','description').all()) if game_obj.options else [],
                }) 
                status_value = ""
            
            return Response({'data': game_list}, status=status.HTTP_200_OK)
        except:
            import traceback 
            traceback.print_exc()
            return Response({'error': "No post found"}, status=status.HTTP_404_NOT_FOUND)

class GetUserGameListAdmin(APIView):
    serializer_class = GameSerializer
    """
        API endpoint that shows all games in 
    """
    permission_classes = [IsAuthenticated]
    def get(self, request,student_id, *args, **kwargs):
        try:
            game_type = request.GET.get('game_type', None)
            game_mode = request.GET.get('game_mode', None)
            collage_name = self.request.GET.get('campus_name', None)
            game_status = self.request.GET.get('game_status', None)
            game_list = []
            
            user_start_games = GameUser.objects.filter(user__id=student_id)

            if game_mode:
                user_start_games = user_start_games.filter(game__mode=game_mode)

            if game_type:
                user_start_games = user_start_games.filter(game__game_type__id=game_type)
            
            if collage_name:
                user_start_games = user_start_games.filter(game__collage_name=collage_name)
            
            if game_status:
                user_start_games = user_start_games.filter(game__status=game_status)
            
            user_start_games = user_start_games.all().order_by('game__level')

            for game_ob in user_start_games:
                game_list.append({
                    "id":game_ob.game.pk,
                    "tittle":game_ob.game.tittle,
                    "description":game_ob.game.description,
                    "game_mode":game_ob.game.mode,
                    "status":game_ob.status,
                    "answer_value":game_ob.answer_value,
                })
            
            return Response({'data': game_list}, status=status.HTTP_200_OK)
        except:
            # import traceback 
            # traceback.print_exc()
            return Response({'error': "No post found"}, status=status.HTTP_404_NOT_FOUND)


class GameCurrentLevel(APIView):
    permission_classes = [IsActiveStudent]
    serializer_class = GameSerializer
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            game_data = {}
            game_obj = GameUser.objects.filter(user=user).select_related('game').last()
            level_count = Games.objects.filter(mode=game_obj.game.mode,collage_name=game_obj.game.collage_name,id__lte=game_obj.game.pk).count()
            if game_obj:
                game_data = {
                    "game_tittle":game_obj.game.tittle,
                    "game_level":level_count,
                    "game_description":game_obj.game.description,
                    "game_type":game_obj.game.game_type.tittle,
                    "game_answer_value":game_obj.game.answer_value,
                    "game_mode":game_obj.game.mode,
                    "user_notes":game_obj.notes,
                    "user_game_status":game_obj.status,
                }

            return Response({'message': "Game Details.",'data':game_data}, status=status.HTTP_200_OK)
        except:
            return Response({'error': "No data found"}, status=status.HTTP_404_NOT_FOUND)
        
class GameLevelUpdate(APIView):
    permission_classes = [IsActiveStudent]
    serializer_class = GameSerializer
    def get(self, request, *args, **kwargs):
        try:
            game_id = request.GET.get('game_id')
            game_data = {}
            game_obj = GameUser.objects.filter(game__id=game_id).select_related('game').first()
            if game_obj:
                game_data = {
                    "game_tittle":game_obj.game.tittle,
                    "game_level":game_obj.game.level,
                    "game_description":game_obj.game.description,
                    "game_options":game_obj.game.options.values().all(),
                    "game_type":game_obj.game.game_type.tittle,
                    "game_qrcode":game_obj.game.qr_code,
                    "game_answer_value":game_obj.game.answer_value,
                    "game_mode":game_obj.game.mode,
                    "user_notes":game_obj.notes,
                    "user_game_status":game_obj.status,
                }
            return Response({'message': "Game Details.",'data':game_data}, status=status.HTTP_200_OK)
        except:
            return Response({'error': "No data found"}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, *args, **kwargs):
        try:
            game_id = request.data['game_id']
            # game_status = request.data['status']
            game_notes = request.data['notes']
            answer_value = str(request.data['answer_value'])
            user = request.user
            game_obj = Games.objects.filter(id=game_id).first()
            user_game = GameUser.objects.filter(user=user,game=game_obj).first()
            if game_obj.mode == "qr" and game_obj.answer_value != answer_value:
                return Response({'message': "Please submit valid QR."}, status=status.HTTP_400_BAD_REQUEST)

            if game_obj.mode != "qr" and user_game:
                return Response({'message': "This game is already completed."}, status=status.HTTP_400_BAD_REQUEST)
            
            if user_game and user_game.answer_value == game_obj.answer_value:
                return Response({'message': "This game is already completed."}, status=status.HTTP_400_BAD_REQUEST)
            
            game_success = 0
            game_status = "F"
            answer_value_qr = answer_value
            answer_value = answer_value.lower()
            if game_obj.mode != "image" and (game_obj.answer_value == answer_value or game_obj.answer_value == answer_value_qr) :
                game_status = "C"
                game_success = 1
            
            if game_obj.mode == "image":
                game_status = "C"
                game_success = 1

            if not user_game:
                user_game = GameUser.objects.create(
                    user=user,
                    game=game_obj,
                    notes=game_notes,
                    status=game_status,
                    answer_value = answer_value
                )
            else:
                if game_obj.mode == "qr":
                    user_game.answer_value = answer_value
                    user_game.save()

            
            if user_game:
                user_score = GamesScoreBoard.objects.filter(student=user,game_level=game_obj.game_type).first()
                if not user_score:
                    GamesScoreBoard.objects.create(
                        student=user_game.user,
                        game_level=user_game.game.game_type,
                        total_games=Games.objects.filter(game_type=game_obj.game_type,collage_name=game_obj.collage_name).count(),
                        success_games=1,
                        played_games=game_success
                    )
                else:

                    user_score.success_games = int(user_score.success_games) + 1
                    user_score.played_games = int(user_score.played_games) + game_success
                    user_score.save()

            return Response({'message': "level updated."}, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_404_NOT_FOUND)

class GameImageStatusUpdate(APIView):
    permission_classes = [IsActiveStudent]
    serializer_class = GameSerializer
        
    def post(self, request, *args, **kwargs):
        try:
            game_id = request.data['game_id']
            student_id = request.data['student_id']
            game_status = request.data['game_status']

            user_game = GameUser.objects.filter(user__id=student_id,game__id=game_id,game__options="image").first()
            if user_game:
                user_game.status = game_status
                user_game.save()
            else:
                return Response({'message': "Game not found. Please check payload."}, status=status.HTTP_200_OK)
                

            return Response({'message': "Status updated."}, status=status.HTTP_200_OK)
        except:
            return Response({'error': "No post found"}, status=status.HTTP_404_NOT_FOUND)


class FileUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = UserUploadSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    

class GetUserGameDetails(APIView):
    serializer_class = GamesTypeSerializer
    permission_classes = [IsActiveStudent]
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            collage_name = user.collage_name
            game_type_objs = GamesType.objects.all()
            game_data = []
            open_status = False
            for game_type_obj in game_type_objs:
                game_type_data = {
                    "tittle":game_type_obj.tittle,
                    "description":game_type_obj.description,
                }
                game_user_count = GameUser.objects.filter(user=request.user,game__game_type=game_type_obj).count()
                game_count = Games.objects.filter(game_type=game_type_obj,collage_name=collage_name).count()
                if game_user_count == game_count :
                    game_type_data["status"] = "C"
                elif not open_status:
                    open_status = True
                    game_type_data["status"] = "O"
                else:
                    game_type_data["status"] = ""

                game_data.append(game_type_data)

            return Response({'data': game_data}, status=status.HTTP_200_OK)
        except:
            return Response({'error': "No post found"}, status=status.HTTP_404_NOT_FOUND)

class GameUserViewSet(viewsets.ModelViewSet):
    """
    An API endpoint that allows Games Options to answer with one of the options. 
    """
    permission_classes = [IsAuthenticated]
    queryset = GameUser.objects.all()
    serializer_class = GameUserSerializer
    http_method_names = ['get',]

from django.db.models import Count,Subquery

class GamesScoreBoardView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            campus_name = user.collage_name

            total_mcq_questions = Games.objects.filter(collage_name=campus_name,mode="options").count()
            total_qr_questions = Games.objects.filter(collage_name=campus_name,mode="qr").count()
            total_image_questions = Games.objects.filter(collage_name=campus_name,mode="image").count()

            mcq_questions = list(GamesScoreBoard.objects.filter(game_level__tittle="Level 1",success_games__gte=total_mcq_questions,student__collage_name=campus_name).values_list('student__id',flat=True))
            qr_questions = list(GamesScoreBoard.objects.filter(game_level__tittle="Level 3",success_games__gte=total_qr_questions,student__id__in=mcq_questions,student__collage_name=campus_name).values_list('student__id',flat=True))
            image_questions = list(GamesScoreBoard.objects.filter(game_level__tittle="Level 2",success_games__gte=total_image_questions,student__id__in=qr_questions,student__collage_name=campus_name).values_list('student__id',flat=True).order_by('update'))

            student_obj = Student.objects.filter(id__in=image_questions).values('email','username','contact_number').all()

            return Response({'data': student_obj}, status=status.HTTP_200_OK)
        except:
            import traceback; traceback.print_exc();
            return Response({'error': "No post found"}, status=status.HTTP_404_NOT_FOUND)
        

class GamesScoreBoardClean(APIView):
    permission_classes = [IsAuthenticated]
    queryset = GamesScoreBoard.objects.all()
    serializer_class = GamesScoreBoardSerializer
    def get(self, request, *args, **kwargs):
        try:
            Student.objects.filter(is_staff=False,is_superuser=False,is_deleted=False).update(is_deleted=True)
            game_obj = GamesScoreBoard.objects.all()
            game_obj.delete()
            game_usr = GameUser.objects.all()
            game_usr.delete()
            return Response({'data': {},'message': "All Games Reset Successfull."}, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GamesScoreBoardList(generics.ListAPIView):
    queryset = GamesScoreBoard.objects.all()
    serializer_class = GamesScoreBoardSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        
        student = request.GET.get('student', None)
        if student:
            self.queryset = self.queryset.filter(student__id=student)

        game_level = request.GET.get('game_level', None)
        if game_level:
            self.queryset = self.queryset.filter(game_level__id=game_level)

        response_data = super().get(self, request, *args, **kwargs)
        return Response({'message':"Student List.",'status': True,"data":response_data.data})