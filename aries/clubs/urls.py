from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.clubs, name='clubs-home'),
    path('register/', views.clan_register, name='clan_register'),
    path('login/', views.clan_login, name='clan_login'),
    path('logout/', views.clan_logout, name='clan_logout'),
    path('dashboard/', views.clan_dashboard, name='clan_dashboard')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)