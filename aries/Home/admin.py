from clubs.models import Clans
from users.models import Profile
from django.contrib import admin
from tournaments.models import ClanTournament, IndiTournament

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username']  # Allow search by username in the admin interface

@admin.register(ClanTournament)
class ClanTournamentAdmin(admin.ModelAdmin):
    autocomplete_fields = ['teams']  
    def save_related(self, request, form, formsets, change):
        """
        Save related objects and ensure matches are created after the form is saved.
        """
        super().save_related(request, form, formsets, change)
        try:
            form.instance.create_matches()  # Call the custom `create_matches` logic
        except Exception as e:
            self.message_user(request, f"Error creating matches: {e}", level='error')

@admin.register(IndiTournament)
class IndiTournamentAdmin(admin.ModelAdmin):
    autocomplete_fields = ['players']  # Enable autocomplete for selecting players

    def save_related(self, request, form, formsets, change):
        """
        Save related objects and ensure matches are created after the form is saved.
        """
        super().save_related(request, form, formsets, change)
        try:
            form.instance.create_matches()  # Call the custom `create_matches` logic
        except Exception as e:
            self.message_user(request, f"Error creating matches: {e}", level='error')

class ProfileInline(admin.TabularInline):
    """
    Inline editing for profiles within the Clans admin interface.
    """
    model = Profile
    extra = 0  # No extra blank forms by default

@admin.register(Clans)
class ClansAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]  # Add profiles as inline objects in the Clans admin
    search_fields = ['clan_name']  # Allow search by clan name in the admin interface



