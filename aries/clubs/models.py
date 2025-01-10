from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.



class Clans(models.Model):
    # Basic Information
    clan_name = models.CharField(max_length=255)
    clan_tag = models.CharField(max_length=10)
    clan_description = models.TextField()
    clan_logo = models.ImageField(upload_to='clan_logos')
    clan_website = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    primary_game = models.CharField(max_length=255, blank=True, null=True) #which games they mainly play
    other_games = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=50)  
    timezone = models.CharField(max_length=50) #the time zone the operate in
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=None)


    # Clan Statistics
    clan_members = models.JSONField(blank=True, null=True) #will try to link to clanMmbers later
    clan_teams = models.TextField(default=0)
    total_matches = models.IntegerField(default=0, editable=False)
    win_rate = models.FloatField(default=0.0, editable=False)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    ranking = models.IntegerField(blank=True, null=True, editable=False)
    average_team_score = models.FloatField(default=0.0, editable=False)
    achievements = models.JSONField(blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)
    is_recruiting = models.BooleanField(default=False)
    recruitment_requirements = models.TextField(blank=True, null=True)
    application_link = models.URLField(blank=True, null=True)
    leaderboard_position = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Clan"
        verbose_name_plural = "Clans"

    def __str__(self):
        return f"{self.clan_name} [{self.clan_tag}] Rank:#{self.leaderboard_position}"