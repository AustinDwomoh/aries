from clubs.models import Clans
from users.models import Profile
from django.contrib import admin
from tournaments.models import ClanTournament,IndiTournament

admin.site.register(Profile)

@admin.register(ClanTournament)
class ClanTournamentAdmin(admin.ModelAdmin):
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Ensure matches are created after related objects are saved
        form.instance.create_matches()


@admin.register(IndiTournament)
class IndiTournamentAdmin(admin.ModelAdmin):
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Ensure matches are created after related objects are saved
        form.instance.create_matches()


class ProfileInline(admin.TabularInline):
    model = Profile
    extra = 0

# Custom admin for Clans
@admin.register(Clans)
class ClansAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]


