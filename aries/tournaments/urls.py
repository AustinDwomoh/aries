from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.tours, name='tournament-home'),  # Homepage for tournaments
    path('cvc_tour_view/<int:tour_id>/', views.tours_cvc_view, name='cvc_details'),  # View specific Clan vs Clan tournament
    path('indi_tour_view/<int:tour_id>/', views.tours_indi_view, name='indi_details'),  # View specific Individual tournament
    
    path('create_clan_tournament/', views.create_clan_tournament, name='create_clan_tournament'),  # Create a Clan vs Clan tournament
    path('create_indi_tournament/', views.create_indi_tournament, name='create_indi_tournament'),  # Create an Individual tournament
    
    path('update_indi_tournament/<int:tour_id>/', views.update_indi_tour, name='update_indi_tournament'),  # Update Individual tournament
    path('update_clan_tournament/<int:tour_id>/', views.update_clan_tour, name='update_clan_tournament'),  # Update Clan vs Clan tournament
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
