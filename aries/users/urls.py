from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Path for the home page of the user profile
    path('', views.profile, name='user-home'),
    
    # Path to view a list of all gamers
    path('gamers/', views.all_gamers, name="gamers"),
    
    # Path to view the details of a specific gamer, using their player_id as a dynamic URL parameter
    path('gamer_view/<int:player_id>/', views.gamer_view, name='player_details'),
    
    # Path to edit the user's profile
    path('edit/', views.edit_profile, name="edit_profile")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)