from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.tours, name='tournament-home'),
    path('cvc_tour_veiw/<int:tour_id>/', views.tours_cvc_view, name='cvc_details'),
    path('indi_tour_veiw/<int:tour_id>/', views.tours_indi_view, name='indi_details'),
    path('create_clan_tournament/', views.create_clan_match, name='create_clan_tournament'),
    path('create_indi_tournament/', views.create_indi_tournament, name='create_indi_tournament'),
    path('update_indi_tournament/<int:tour_id>/', views.update_indi_tour, name='update_indi_tournament'),
    path('update_clan_tournament/<int:tour_id>/', views.update_clan_tour, name='update_clan_tournament'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)