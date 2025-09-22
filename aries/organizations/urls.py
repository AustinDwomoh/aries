from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    # Organization CRUD
    path('', views.OrganizationListCreateView.as_view(), name='organization-list-create'),
    path('<int:pk>/', views.OrganizationDetailView.as_view(), name='organization-detail'),
    
    # Organization actions
    path('<int:pk>/join/', views.join_organization, name='join-organization'),
    path('<int:pk>/leave/', views.leave_organization, name='leave-organization'),
    path('<int:pk>/follow/', views.follow_organization, name='follow-organization'),
    path('<int:pk>/unfollow/', views.unfollow_organization, name='unfollow-organization'),
    path('<int:pk>/members/', views.organization_members, name='organization-members'),
    path('<int:pk>/reputation/', views.organization_reputation, name='organization-reputation'),
    
    # Member management
    path('<int:pk>/members/<int:user_id>/', views.update_member_role, name='update-member-role'),
    path('<int:pk>/members/<int:user_id>/remove/', views.remove_member, name='remove-member'),
]
