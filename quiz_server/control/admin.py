from django.contrib import admin
from control.models import Game, Question, Answer_option, Vote

# Register your models here.

admin.site.register(Game)
admin.site.register(Question)
admin.site.register(Answer_option)
admin.site.register(Vote)