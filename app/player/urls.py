from django.urls import path
from . import views


app_name = 'player'

urlpatterns = [
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('player/', views.player_page, name='player_page'),
]