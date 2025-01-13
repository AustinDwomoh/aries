from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.tours, name='tournament-home'),
    path('clan_match/<int:match_id>/input_scores/', views.input_clan_scores, name='input_clan_scores'),
    path('indi_match/<int:match_id>/input_scores/', views.input_indi_scores, name='input_indi_scores'),
    path('clan-tournament/create/', views.create_clan_tournament, name='create_clan_tournament'),
    path('clan-tournament/', views.list_clan_tournaments, name='list_clan_tournaments'),
    path('indi-tournament/create/', views.create_indi_tournament, name='create_indi_tournament'),
    path('indi-tournament/', views.list_indi_tournaments, name='list_indi_tournaments'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)