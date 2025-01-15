from clubs.models import Clans
from users.models import Profile
from django.contrib import admin
from tournaments.models import ClanTournament,IndiTournament

admin.site.register(Profile)

""" @admin.register(ClanMatch)
class ClanMatchAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # Ensure both teams are assigned before saving the match
        if not obj.team_1 or not obj.team_2:
            raise ValueError("Both teams must be assigned for a match.")
        super().save_model(request, obj, form, change)
 """
@admin.register(ClanTournament)
class ClanTournamentAdmin(admin.ModelAdmin):
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Ensure matches are created after related objects are saved
        form.instance.create_matches()



#admin.site.register(IndiMatch)
admin.site.register(IndiTournament)

class ProfileInline(admin.TabularInline):
    model = Profile
    extra = 0

# Custom admin for Clans
@admin.register(Clans)
class ClansAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]


