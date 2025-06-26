"""
URL configuration for aries project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path,include
from users import views as user_veiws
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),#admin url
    path('', include('Home.urls') ),#index url
    path('clans/', include('clans.urls')),#url that links to club link
    path('register/',user_veiws.register,name='register'),#url to create account
    path('login/',user_veiws.CustomLoginView.as_view(template_name='users/login.html'),name='login'),#url to login to user account
    path('logout/',user_veiws.logout_view,name='logout'),
    path('users/', include('users.urls')),#url that links to user, gamers
    path('tournaments/',include('tournaments.urls')),#url that links to tours,
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)#to allow the media files to be saved and accesed