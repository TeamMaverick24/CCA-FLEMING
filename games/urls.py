from django.urls import include, path
from rest_framework import routers
from .views import *

app_name = "users"

router = routers.DefaultRouter()
router.register("type", GamesTypeViewSet)
router.register("options", GamesOptionsViewSet)   
router.register("", GamesViewSet)

urlpatterns = [
    path('user-game-list', GetUserGameList.as_view()),    
    path('user-game-update', GameLevelUpdate.as_view()),    
]
