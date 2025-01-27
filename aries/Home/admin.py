from clubs.models import Clans, ClanStats
from users.models import Profile, PlayerStats
from orgs.models import Organization
from django.contrib import admin
from tournaments.models import ClanTournament, IndiTournament

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Profile model.
    Allows searching profiles by the associated username.
    """
    search_fields = ['user__username']  # Enable search by username in the admin interface

@admin.register(ClanTournament)
class ClanTournamentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ClanTournament model.
    Supports autocomplete for selecting teams and handles match creation after saving.
    """
    autocomplete_fields = ['teams']  # Enable autocomplete for selecting teams

    def save_related(self, request, form, formsets, change):
        """
        Override the save_related method to create matches after saving the tournament.
        """
        super().save_related(request, form, formsets, change)
        try:
            form.instance.create_matches()  # Call the custom `create_matches` method
        except Exception as e:
            self.message_user(request, f"Error creating matches: {e}", level='error')  # Show error message if match creation fails

@admin.register(IndiTournament)
class IndiTournamentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the IndiTournament model.
    Supports autocomplete for selecting players and handles match creation after saving.
    """
    autocomplete_fields = ['players']  # Enable autocomplete for selecting players

    def save_related(self, request, form, formsets, change):
        """
        Override the save_related method to create matches after saving the tournament.
        """
        super().save_related(request, form, formsets, change)
        try:
            form.instance.create_matches()  # Call the custom `create_matches` method
        except Exception as e:
            self.message_user(request, f"Error creating matches: {e}", level='error')  # Show error message if match creation fails

class ProfileInline(admin.TabularInline):
    """
    Inline editing for the Profile model within the Clans admin interface.
    Allows editing profiles directly from the Clans admin page.
    """
    model = Profile
    extra = 0  # No extra blank forms displayed by default


@admin.register(Clans)
class ClansAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Clans model.
    Supports inline editing of profiles and searching by clan name.
    """
    inlines = [ProfileInline]  # Add ProfileInline for editing profiles within the Clans admin
    search_fields = ['clan_name']  # Enable search by clan name in the admin interface


# Register additional models with the default admin configuration
admin.site.register(Organization)
admin.site.register(ClanStats)
admin.site.register(PlayerStats)