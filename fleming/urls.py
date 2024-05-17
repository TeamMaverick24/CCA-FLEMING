"""fleming URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from dh_user.urls import router as UserRouter
from games.urls import router as gameRouter

from drf_spectacular.views import (
    SpectacularSwaggerView,
    SpectacularAPIView,
)

urlpatterns = [

    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('', SpectacularSwaggerView.as_view(url_name='api-schema'),name='api-docs'),

    path('admin/', admin.site.urls),

    path('api/student/', include(UserRouter.urls)),
    path('api/game/', include(gameRouter.urls)),

    path('', include("games.urls")),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
