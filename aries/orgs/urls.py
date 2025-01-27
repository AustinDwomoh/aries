from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Home page for organizations
    path('', views.organisation, name='organisation-home'),

    # URL for organization registration
    path('register/', views.org_register, name='org_register'),

    # URL for organization login
    path('login/', views.org_login, name='org_login'),

    # URL for organization logout
    path('logout/', views.org_logout, name='org_logout'),

    # URL for organization dashboard
    path('dashboard/', views.org_dashboard, name='org_dashboard'),

    # URL for viewing details of a specific organization
    path('org_veiw/<int:org_id>/', views.org_view, name='org_details'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
