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

    # Clan details page (view specific clan by ID)
    path('clan_view/<int:clan_id>/', views.club_view, name='clan_details'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)