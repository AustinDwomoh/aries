from django.urls import path 
from . import views  
from django.conf import settings  
from django.conf.urls.static import static  
urlpatterns = [
    # Home page for clubs/clans
    path('', views.clubs, name='clubs-home'),

    # Clan registration page
    path('register/', views.clan_register, name='clan_register'),

    # Clan login page
    path('login/', views.clan_login, name='clan_login'),

    # Clan logout page
    path('logout/', views.clan_logout, name='clan_logout'),

    # Clan dashboard page (for logged-in clans)
    path('dashboard/', views.clan_dashboard, name='clan_dashboard'),

    path('add_remove/', views.add_remove_players, name='update_list'),
    path('add_remove_player/', views.approve_reject, name='update_player_list'),
    
    # Clan details page (view specific clan by ID)
    path('clan_view/<int:clan_id>/', views.club_view, name='clan_details'),
    path('<str:action>/<str:followed_model>/<int:followed_id>/', views.club_follow_unfollow, name='clan_follow_unfollow'),
    #request to join a clan
    path("join/<int:clan_id>/", views.request_to_join_clan, name="request_to_join_clan"),

    #leave clan
    path("leave/<int:clan_id>/", views.leave_clan, name="leave_clan"),

    #change req state
    path("change/<int:clan_id>/", views.change_recruitment_state,name="change_recruitment_state"),

    path("desc_change/<int:clan_id>/", views.change_description,name="change_description"),
   
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)