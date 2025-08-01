from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
     # Home page 
    path('',views.home, name ='Home'),

     # About page 
    path('about/',views.about, name ='About'),
   
   path('2200/', views.trigger_error_view)

]




# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

