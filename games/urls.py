from django.urls import include, path
from rest_framework import routers
from .views import *

app_name = "users"

router = routers.DefaultRouter()
router.register("type", GamesTypeViewSet)
router.register("options", GamesOptionsViewSet)   
router.register("", GamesViewSetModel)

urlpatterns = [
    path('game', GamesViewSet.as_view()),    
    path('game-user', GameUserViewSet.as_view({'get': 'list'})),    
    path('user-game-lists', GetUserGameList.as_view()),    
    path('user-game-list/<str:game_level>', GetUserGameListNew.as_view()),    
    path('admin-user-game-list/<str:student_id>', GetUserGameListAdmin.as_view()),    
    path('user-game-type', GetUserGameDetails.as_view()),    
    path('user-game-update', GameLevelUpdate.as_view()),    
    path('admin-game-update', GameImageStatusUpdate.as_view()),    

    path('file-update', FileUploadAPIView.as_view()),    

    path('user-score', GamesScoreBoardView.as_view()), 

    path('game-reset', GamesScoreBoardClean.as_view()),    
    path('current-level', GameCurrentLevel.as_view()),   

    path('game-scorebord-list', GamesScoreBoardList.as_view()),   
     
]
