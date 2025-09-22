from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Organization, 
    OrganizationMember, 
    OrganizationJoinRequest, 
    OrganizationSocialLink,
    OrganizationReputation
)


@admin.register(Organization)
class OrganizationAdmin(UserAdmin):
    """Admin interface for Organization model."""
    list_display = ['name', 'tag', 'email', 'organization_type', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['organization_type', 'is_verified', 'is_active', 'country', 'date_joined']
    search_fields = ['name', 'tag', 'email', 'description']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('name', 'tag', 'email', 'password')}),
        ('Organization Info', {'fields': ('description', 'logo', 'profile_picture', 'website', 'organization_type')}),
        ('Gaming Info', {'fields': ('primary_game', 'other_games', 'country')}),
        ('Organizer Capabilities', {'fields': ('can_host_tournaments', 'can_sponsor_events', 'can_manage_prizes', 'can_verify_teams')}),
        ('Business Info', {'fields': ('business_license', 'tax_id', 'contact_phone', 'established_date')}),
        ('Financial Info', {'fields': ('total_prize_money_distributed', 'total_tournaments_hosted', 'average_tournament_size')}),
        ('Status', {'fields': ('is_verified', 'is_active', 'is_staff')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined', 'last_login')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'tag', 'email', 'password1', 'password2', 'organization_type'),
        }),
    )
    
    readonly_fields = ['date_joined']


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    """Admin interface for OrganizationMember model."""
    list_display = ['user', 'organization', 'role', 'joined_at', 'is_active']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'user__email', 'organization__name']
    ordering = ['-joined_at']


@admin.register(OrganizationJoinRequest)
class OrganizationJoinRequestAdmin(admin.ModelAdmin):
    """Admin interface for OrganizationJoinRequest model."""
    list_display = ['user', 'organization', 'status', 'requested_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['user__username', 'user__email', 'organization__name']
    ordering = ['-requested_at']
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Approve selected join requests."""
        for join_request in queryset.filter(status='pending'):
            join_request.approve()
        self.message_user(request, f"{queryset.count()} join requests approved.")
    approve_requests.short_description = "Approve selected join requests"
    
    def reject_requests(self, request, queryset):
        """Reject selected join requests."""
        queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"{queryset.count()} join requests rejected.")
    reject_requests.short_description = "Reject selected join requests"


@admin.register(OrganizationSocialLink)
class OrganizationSocialLinkAdmin(admin.ModelAdmin):
    """Admin interface for OrganizationSocialLink model."""
    list_display = ['organization', 'link_type', 'url']
    list_filter = ['link_type']
    search_fields = ['organization__name', 'url']


@admin.register(OrganizationReputation)
class OrganizationReputationAdmin(admin.ModelAdmin):
    """Admin interface for OrganizationReputation model."""
    list_display = ['organization', 'reputation_score', 'total_events_organized', 'is_verified_organizer', 'verification_level']
    list_filter = ['is_verified_organizer', 'verification_level']
    search_fields = ['organization__name']
    readonly_fields = ['reputation_score', 'total_events_organized', 'total_participants_reached']
