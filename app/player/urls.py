from django.urls import path
from . import views


app_name = 'player'

urlpatterns = [
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('api/users/', views.get_users, name='get_users'),
    path('api/users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('api/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('api/users/<int:user_id>/change-password/', views.change_password, name='change_password'),
    path('api/users/<int:user_id>/assign-role/', views.assign_role, name='assign_role'),
    path('player/', views.player_page, name='player_page'),
]