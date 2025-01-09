from django.contrib import admin
from clubs.models import Clans
from users.models import ClanMembers

# Register your models here. all models for admisn will be registered here
admin.site.register(Clans)
admin.site.register(ClanMembers)