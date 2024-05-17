from rest_framework import routers
from dh_user.views import UserViewSet
from django.urls import include, path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
# from . import views

app_name = "users"

router = routers.DefaultRouter()
router.register("", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]
