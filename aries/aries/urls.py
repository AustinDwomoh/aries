"""
ARIES - Centralized URL Configuration
=====================================

This is the main URL configuration for the Aries project.
All API endpoints are centralized here for better organization and maintenance.

URL Structure:
- /admin/ - Django admin interface
- /jet/ - Django JET admin interface  
- /api/ - All API endpoints (REST API only)
- /api/err/ - Test endpoint for error monitoring

API Endpoints Organization:
- Authentication & Users: /api/auth/*, /api/users/*
- Organizations: /api/organizations/*
- Tournaments: /api/tournaments/*
- Clans: /api/clans/*
- Home/Stats: /api/home/*
- Verification: /api/verify/*

Note: This is a pure API backend - no template-based views.
Frontend is handled by React/TypeScript application.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

# Import API views for direct URL patterns
from users import api_views as user_views
from Home import api_views as home_views
from organizations import views as org_views
from tournaments import api_views as tournament_views
from clans import api_views as clan_views
from scripts.error_handle import ErrorHandler


def trigger_error_view(request):
    """
    Test view to deliberately trigger an error for monitoring/debugging.
    Used for testing error handling and monitoring systems.
    """
    print("[URLS] Error test endpoint accessed")
    try:
        1 / 0
    except Exception as e:
        print(f"[URLS] Error test triggered: {e}")
        ErrorHandler().handle(e)
        return HttpResponse("Error has been logged and admin notified.", status=500)


# =============================================================================
# MAIN URL PATTERNS
# =============================================================================

urlpatterns = [
    # ========================================================================
    # ADMIN INTERFACES
    # ========================================================================
    path('admin/', admin.site.urls),  # Django admin interface
    path('jet/', include('jet.urls')),  # Django JET admin interface
    path('jet/dashboard/', include('jet.dashboard.urls', namespace='jet-dashboard')),  # Django JET dashboard

    # ========================================================================
    # API ENDPOINTS - AUTHENTICATION & USERS
    # ========================================================================
    # Authentication endpoints
    path('api/auth/login/', user_views.LoginAPIView.as_view(), name='api-login'),
    path('api/auth/register/', user_views.RegisterAPIView.as_view(), name='api-register'),
    path('api/auth/logout/', user_views.LogoutAPIView.as_view(), name='api-logout'),
    path('api/auth/me/', user_views.CurrentUserAPIView.as_view(), name='api-current-user'),
    
    # Email verification endpoints
    path('api/auth/verify-email/<str:model_type>/<str:uidb64>/<str:token>/', 
         user_views.VerifyEmailAPIView.as_view(), name='api-verify-email'),
    path('api/auth/verify-otp/', user_views.VerifyOTPAPIView.as_view(), name='api-verify-otp'),
    path('api/auth/resend-verification/', user_views.ResendVerificationAPIView.as_view(), name='api-resend-verification'),
    path('api/auth/verification-pending/', user_views.VerificationPendingAPIView.as_view(), name='api-verification-pending'),
    
    # User profile endpoints
    path('api/users/<int:user_id>/profile/', user_views.UserProfileAPIView.as_view(), name='api-user-profile'),
    path('api/users/<int:user_id>/follow/', user_views.FollowUserAPIView.as_view(), name='api-follow-user'),
    path('api/users/<int:user_id>/unfollow/', user_views.UnfollowUserAPIView.as_view(), name='api-unfollow-user'),

    # ========================================================================
    # API ENDPOINTS - ORGANIZATIONS
    # ========================================================================
    # Organization CRUD operations
    path('api/organizations/', org_views.OrganizationListCreateView.as_view(), name='api-organization-list'),
    path('api/organizations/<int:pk>/', org_views.OrganizationDetailView.as_view(), name='api-organization-detail'),
    
    # Organization actions
    path('api/organizations/<int:pk>/join/', org_views.join_organization, name='api-join-organization'),
    path('api/organizations/<int:pk>/leave/', org_views.leave_organization, name='api-leave-organization'),
    path('api/organizations/<int:pk>/follow/', org_views.follow_organization, name='api-follow-organization'),
    path('api/organizations/<int:pk>/unfollow/', org_views.unfollow_organization, name='api-unfollow-organization'),
    path('api/organizations/<int:pk>/members/', org_views.organization_members, name='api-organization-members'),
    path('api/organizations/<int:pk>/reputation/', org_views.organization_reputation, name='api-organization-reputation'),
    
    # Organization member management
    path('api/organizations/<int:pk>/members/<int:user_id>/', org_views.update_member_role, name='api-update-member-role'),
    path('api/organizations/<int:pk>/members/<int:user_id>/remove/', org_views.remove_member, name='api-remove-member'),

    # ========================================================================
    # API ENDPOINTS - TOURNAMENTS
    # ========================================================================
    # Tournament CRUD operations
    path('api/tournaments/', tournament_views.TournamentListCreateAPIView.as_view(), name='api-tournament-list'),
    path('api/tournaments/<int:pk>/', tournament_views.TournamentDetailAPIView.as_view(), name='api-tournament-detail'),
    
    # Tournament actions
    path('api/tournaments/<int:pk>/join/', tournament_views.JoinTournamentAPIView.as_view(), name='api-join-tournament'),
    path('api/tournaments/<int:pk>/leave/', tournament_views.LeaveTournamentAPIView.as_view(), name='api-leave-tournament'),
    path('api/tournaments/<int:pk>/matches/', tournament_views.TournamentMatchesAPIView.as_view(), name='api-tournament-matches'),
    path('api/tournaments/<int:pk>/matches/<int:match_id>/', tournament_views.UpdateMatchResultAPIView.as_view(), name='api-update-match'),

    # ========================================================================
    # API ENDPOINTS - CLANS
    # ========================================================================
    # Clan CRUD operations
    path('api/clans/', clan_views.ClanListCreateAPIView.as_view(), name='api-clan-list'),
    path('api/clans/<int:pk>/', clan_views.ClanDetailAPIView.as_view(), name='api-clan-detail'),
    
    # Clan actions
    path('api/clans/<int:pk>/join/', clan_views.JoinClanAPIView.as_view(), name='api-join-clan'),
    path('api/clans/<int:pk>/leave/', clan_views.LeaveClanAPIView.as_view(), name='api-leave-clan'),
    path('api/clans/<int:pk>/members/', clan_views.ClanMembersAPIView.as_view(), name='api-clan-members'),
    path('api/clans/<int:pk>/members/<int:user_id>/', clan_views.UpdateMemberRoleAPIView.as_view(), name='api-update-member-role'),
    path('api/clans/<int:pk>/members/<int:user_id>/remove/', clan_views.RemoveMemberAPIView.as_view(), name='api-remove-member'),
    path('api/clans/<int:pk>/join-requests/', clan_views.ClanJoinRequestsAPIView.as_view(), name='api-clan-join-requests'),
    path('api/clans/<int:pk>/join-requests/<int:request_id>/approve/', clan_views.ApproveJoinRequestAPIView.as_view(), name='api-approve-join-request'),
    path('api/clans/<int:pk>/join-requests/<int:request_id>/reject/', clan_views.RejectJoinRequestAPIView.as_view(), name='api-reject-join-request'),

    # ========================================================================
    # API ENDPOINTS - HOME & STATISTICS
    # ========================================================================
    # Home data and statistics
    path('api/home/stats/', home_views.HomeStatsAPIView.as_view(), name='api-home-stats'),
    path('api/home/follow/<str:model>/<int:profile_id>/<str:ftype>/', home_views.FollowListAPIView.as_view(), name='api-follow-list'),
    path('api/home/ads.txt', home_views.AdsTxtAPIView.as_view(), name='api-ads-txt'),

    # ========================================================================
    # LEGACY VERIFICATION ENDPOINTS (for backward compatibility)
    # ========================================================================
    # These endpoints maintain compatibility with existing verification flows
    path('api/verify/<str:model_type>/<uidb64>/<token>/', user_views.VerifyEmailAPIView.as_view(), name='verify_email'),
    path('api/verify-otp/', user_views.VerifyOTPAPIView.as_view(), name='verify_otp'),
    path('api/verify/pending/', user_views.VerificationPendingAPIView.as_view(), name='verification_pending'),
    path('api/verify/resend/', user_views.ResendVerificationAPIView.as_view(), name='resend_verification'),

    # ========================================================================
    # UTILITY & TESTING ENDPOINTS
    # ========================================================================
    # Test endpoint for error monitoring and debugging
    path('api/err/', trigger_error_view, name='api-error-test'),
]

if settings.DEBUG:
    # Serve media files via Django during development (not suitable for production)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
