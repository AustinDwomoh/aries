from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.tours, name='tournament-home'),
    path('cvc_tour_veiw/<int:tour_id>/', views.tours_cvc_view, name='cvc_details'),
    path('indi_tour_veiw/<int:tour_id>/', views.tours_indi_view, name='indi_details')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)