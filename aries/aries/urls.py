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
#from jet.dashboard.dashboard_modules import google_analytics_views

urlpatterns = [
    path('jet/', include('jet.urls')),  # Django JET admin interface
    path('jet/dashboard/', include('jet.dashboard.urls', namespace='jet-dashboard')),  # Django JET dashboard
    path('admin/', admin.site.urls),  # Default Django admin interface
    path('', include('Home.urls')),   # Home app: serves main landing/index pages

    path('clans/', include('clans.urls')),  # Clan management features
    path('register/', user_views.register, name='register'),  # User registration page
    path('login/', user_views.CustomLoginView.as_view(), name='login'),  # Custom login view with extended logic serves both clan and users
    path('logout/', user_views.logout_view, name='logout'),  # Account logout endpoint

    path('users/', include('users.urls')),  # User profiles and related gamer features
    path('tournaments/', include('tournaments.urls')),  # Tournament-related functionality

    # Email verification flow URLs with tokens and OTP verification
    path("verify/<str:model_type>/<uidb64>/<token>/", user_views.verify_email, name="verify_email"),
    path("verify-otp/", user_views.verify_otp, name="verify_otp"),
    path('verify/pending/', user_views.verification_pending, name='verification_pending'),
    path('verify/resend/', user_views.resend_verification, name='resend_verification'),

    path('err/', trigger_error_view),  # Test view to deliberately trigger an error for monitoring/debugging

    # Dynamic follow/unfollow toggle for various models identified by type and object ID
    path('follow/<str:action>/<str:model>/<int:obj_id>/', user_views.follow_toggle_view, name="follow-toggle"),
]

if settings.DEBUG:
    # Serve media files via Django during development (not suitable for production)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
