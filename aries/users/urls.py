from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.profile, name='user-home'),
    path('gamers/', views.all_gamers, name="gamers"),
    path('gamer_view/<int:player_id>/', views.gamer_view, name='player_details'),
    path('edit/', views.edit_profile, name="edit_profile"),
    path('<str:action>/<str:followed_model>/<int:followed_id>/', views.follow_unfollow, name='follow_unfollow'),
    

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)