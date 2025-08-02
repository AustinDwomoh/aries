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
from django.urls import path,include
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static
from Home.views import trigger_error_view


urlpatterns = [
    path('admin/', admin.site.urls),#admin url
    path('', include('Home.urls') ),#index url
    path('clans/', include('clans.urls')),#url that links to club link
    path('register/',user_views.register,name='register'),#url to create account
    path('login/',user_views.CustomLoginView.as_view(),name='login'),
    path('logout/',user_views.logout_view,name='logout'),
    path('users/', include('users.urls')),#url that links to user, gamers
    path('tournaments/',include('tournaments.urls')),#url that links to tours,
    path("verify/<uidb64>/<token>/", user_views.verify_email, name="verify_email"),
    path("verify-otp/", user_views.verify_otp, name="verify_otp"),
    path('verify/pending/', user_views.verification_pending, name='verification_pending'),
    path('verify/resend/', user_views.resend_verification, name='resend_verification'),
       path('err/', trigger_error_view)

] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)#to allow the media files to be saved and accesed