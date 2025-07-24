from django.urls import path 
from . import views  
from django.conf import settings  
from django.conf.urls.static import static  
#app_name = 'clans'
urlpatterns = [
    path('', views.clans, name='clan_home'),
    path('register/', views.clan_register, name='clan_register'),
    path('login/', views.clan_login, name='clan_login'),
    path('logout/', views.clan_logout, name='logout'),
    path('dashboard/', views.clan_dashboard, name='clan_dashboard'),

    # Players management
    path('players/manage/', views.add_remove_players, name='players_manage'),
    path('players/approve_reject/', views.approve_reject, name='players_approve_reject'),

    # Clan detail and actions
    path('<int:clan_id>/', views.clan_view, name='clan_details'),
    path('<str:action>/<str:followed_model>/<int:followed_id>/', views.clan_follow_unfollow, name='clan_follow_unfollow'),
    path('<int:clan_id>/join/', views.request_to_join_clan, name='request_to_join_clan'),
    path('<int:clan_id>/leave/', views.leave_clan, name='leave'),
    path('<int:clan_id>/recruitment/toggle/', views.change_recruitment_state, name='change_recruitment_state'),
    path('<int:clan_id>/description/update/', views.change_description, name='change_description'),
   
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)