from django.contrib import admin
from games.models import *


admin.site.register(GamesType)
admin.site.register(GamesOptions)
admin.site.register(Games)
admin.site.register(GameUser)