from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
     # Home page 
    path('',views.home, name ='Home'),
    path('about/',views.about, name ='About'),
    path("f_/<str:model>/<int:profile_id>/<str:ftype>/", views.follow_list_view, name="follow-list"),
    path('ads.txt', views.ads_txt ),
]




# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

