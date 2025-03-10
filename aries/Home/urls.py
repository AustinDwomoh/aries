from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
     # Home page 
    path('',views.home, name ='Home'),

     # About page 
    path('about/',views.about, name ='About'),
    path('follow/user/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/user/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('follow/club/<int:club_id>/', views.follow_club, name='follow_club'),
    path('unfollow/club/<int:club_id>/', views.unfollow_club, name='unfollow_club'),

]




# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

