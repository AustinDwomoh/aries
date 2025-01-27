from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from clubs.models import Clans  
import os,json

class Profile(models.Model):
    """
    Profile model to extend Django's built-in User model.
    Each user has a single profile with optional clan membership, social links, 
    a profile picture, and a role within a clan.
    """
    ROLE_CHOICES = [('admin', 'Admin'),('captain', 'Captain'),('member', 'Member'),]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clan = models.ForeignKey(Clans,on_delete=models.CASCADE, null=True, blank=True, related_name="members")
    social_links = models.JSONField(blank=True, null=True) 
    profile_picture = models.ImageField(default="default.jpg",upload_to='profile_pics')
    role = models.CharField(max_length=100,choices=ROLE_CHOICES, blank=True, null=True)
    
    def get_social_link(self, platform):
        """
        Retrieves a specific social media link if it exists in the JSON field.
        :param platform: The name of the social media platform (e.g., 'twitter', 'discord').
        :return: URL as a string if found, otherwise None.
        """
        return self.social_links.get(platform, "") if self.social_links else None

    def __str__(self):
        return f'{self.user.username}' 
   

class PlayerStats(models.Model):
    """ PlayerStats model to extend Django's built-in User model."""
    user_profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='stats')
    achievements = models.JSONField(blank=True, null=True)
    RANK_CHOICES = [('rookie', 'Rookie'),('prodigy', 'Prodigy'),('veteran', 'Veteran'),('legend', 'Legend'),('superstar', 'Superstar'),('elite', 'Elite'),('mvp', 'MVP'),('world_class', 'World-Class'),]
    rank = models.CharField(max_length=20,choices=RANK_CHOICES,blank=True,null=True,editable=False)
    games_played = models.IntegerField(default=0)
    win_rate = models.FloatField(default=0.0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    total_draws = models.IntegerField(default=0)
    gd = models.IntegerField(default=0)
    gf = models.IntegerField(default=0)
    ga = models.IntegerField(default=0)
    elo_rating = models.FloatField(default=1200, editable=False)
    season = models.CharField(max_length=20, default="2025")
    match_data = models.JSONField(blank=True, null=True, default=dict)

    def set_rank_based_on_elo(self):
        """Set the rank of the player based on the Elo value."""
        if self.elo_rating < 1200:
            self.rank = 'rookie'
        elif self.elo_rating < 1400:
            self.rank = 'prodigy'
        elif self.elo_rating < 1600:
            self.rank = 'veteran'
        elif self.elo_rating < 1800:
            self.rank = 'legend'
        elif self.elo_rating < 2000:
            self.rank = 'superstar'
        elif self.elo_rating < 2200:
            self.rank = 'elite'
        elif self.elo_rating < 2400:
            self.rank = 'mvp'
        else:
            self.rank = 'world_class'

        self.save()

    def get_json_file_path(self):
        """Return the file path for the JSON data."""
        directory = os.path.join(settings.MEDIA_ROOT, 'match_data')
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, f'player_match_data_{self.pk}.json')

    def save_match_data_to_file(self):
        """Save match data to a JSON file if it exists."""
        if not self.match_data:  
            return

        file_path = self.get_json_file_path()
        with open(file_path, 'w') as json_file:
            json.dump(self.match_data, json_file, indent=4)

    def load_match_data_from_file(self):
        """Load match data from the JSON file."""
        file_path = self.get_json_file_path()
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as json_file:
                try:
                    return json.load(json_file)
                except json.JSONDecodeError:
                    return {}
        return {}

    def delete(self, *args, **kwargs):
        """Delete the JSON file when the player stats are deleted."""
        file_path = self.get_json_file_path()
        if os.path.exists(file_path):
            os.remove(file_path)
        super().delete(*args, **kwargs)
