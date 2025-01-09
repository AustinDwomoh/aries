from django.db import models
from django.contrib.auth.models import User
from clubs.models import Clans  

class ClanMembers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ClanMembers")
    clan = models.ForeignKey(Clans, on_delete=models.CASCADE, related_name="ClanMembers")
    role = models.CharField(max_length=100, blank=True, null=True)  # Role in the clan (e.g., "Player", "Coach", "Captain")
    achievements = models.JSONField(blank=True, null=True)  # Notable achievements or accomplishments
    rank = models.IntegerField(null=True, blank=True)  # Player's rank within the clan
    games_played = models.IntegerField(default=0)  # Total games the player has played
    win_rate = models.FloatField(default=0.0)  # Player's win rate (e.g., 75.5 for 75.5%)
    total_wins = models.IntegerField(default=0)  # Total number of wins
    total_losses = models.IntegerField(default=0)  # Total number of losses
    social_links = models.JSONField(blank=True, null=True) 
    profile_picture = models.ImageField(upload_to='static/images/profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def calculate_win_rate(self):
        """Calculate the player's win rate based on wins and losses."""
        if self.total_wins + self.total_losses > 0:
            return (self.total_wins / (self.total_wins + self.total_losses)) * 100
        return 0.0  

    def save(self, *args, **kwargs):
        self.win_rate = self.calculate_win_rate()
        super().save(*args, **kwargs)
