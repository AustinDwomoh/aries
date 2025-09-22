from clans.models import *
from Home.models import Follow
from users.models import Profile, PlayerStats,SocialLink
from django.contrib import admin
from tournaments.models import Tournament

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Profile model.
    Allows searching profiles by the associated username.
    """
    search_fields = ['user__username']  # Enable search by username in the admin interface


class ProfileInline(admin.TabularInline):
    """
    Inline editing for the Profile model within the Clans admin interface.
    Allows editing profiles directly from the Clans admin page.
    """
    model = Profile
    extra = 0  # No extra blank forms displayed by default

@admin.register(Clan)
class ClansAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Clans model.
    Supports inline editing of profiles and searching by clan name.
    """
    inlines = [ProfileInline]  # Add ProfileInline for editing profiles within the Clans admin
    search_fields = ['clan_name']  # Enable search by clan name in the admin interface


# Register additional models with the default admin configuration
admin.site.register(ClanStats)
admin.site.register(PlayerStats)
admin.site.register(ClanJoinRequest)
admin.site.register(Follow)
admin.site.register(SocialLink)