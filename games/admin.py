from django.contrib import admin
from games.models import *


admin.site.register(GamesType)
admin.site.register(GamesOptions)
admin.site.register(GameUser)
admin.site.register(GamesScoreBoard)


class AdminGames(admin.ModelAdmin):
    list_display = ['id','tittle' ,'level','mode','game_type']

admin.site.register(Games,AdminGames)
