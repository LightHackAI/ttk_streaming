from django.urls import path
from . import views


app_name = 'player'

urlpatterns = [
    path('player/', views.player_page, name='player_page')
]