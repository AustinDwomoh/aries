from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.organisation, name='organisation-home'),
    path('register/', views.org_register, name='org_register'),
    path('login/', views.org_login, name='org_login'),
    path('logout/', views.org_logout, name='org_logout'),
    path('dashboard/', views.org_dashboard, name='org_dashboard'),
    path('org_veiw/<int:org_id>/', views.org_view, name='org_details')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
