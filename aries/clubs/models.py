from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
import os, json
from django.conf import settings

class Clans(models.Model):
    """
    Represents a clan in the system. A clan is a group of players who compete together.
    This model stores information about the clan, including its name, tag, description,
    logo, and other relevant details.
    """
    clan_name = models.CharField(max_length=255)
    clan_tag = models.CharField(max_length=10)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    clan_description = models.TextField()
    clan_logo = models.ImageField(default="areis-1.png",upload_to='clan_logos')
    clan_profile_pic = models.ImageField(default="areis-2.jpg",upload_to='clan_profile')
    clan_website = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    primary_game = models.CharField(max_length=255, blank=True, null=True) #which games they mainly play
    other_games = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=50)  
   #S created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    social_links = models.JSONField(blank=True, null=True)
    is_recruiting = models.BooleanField(default=False)
    recruitment_requirements = models.TextField(blank=True, null=True)


    class Meta:
        verbose_name = "Clan"
        verbose_name_plural = "Clans"

    def set_password(self, raw_password):
        """Hash and store the password."""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Check the provided password against the stored hash."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.clan_name}"
    


    
class ClanStats(models.Model):
    """
    Represents statistics and performance metrics for a clan.
    This model is linked to the Clans model via a one-to-one relationship.
    """
    clan = models.OneToOneField(Clans, on_delete=models.CASCADE,related_name='stat')
    total_matches = models.IntegerField(default=0, editable=False)
    win_rate = models.FloatField(default=0.0, editable=False)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    RANK_CHOICES = [('bronze', 'Bronze'),('silver', 'Silver'),('gold', 'Gold'),('platinum', 'Platinum'),('diamond', 'Diamond'),('master', 'Master'),('grandmaster', 'Grandmaster'),('champion', 'Champion'),('invincible', 'Invincible'),]
    ranking = models.CharField(max_length=20,choices=RANK_CHOICES,blank=True,null=True,editable=False)
    gd = models.IntegerField(default=0)
    gf = models.IntegerField(default=0)
    ga = models.IntegerField(default=0)
    average_team_score = models.FloatField(default=0.0, editable=False)
    achievements = models.JSONField(blank=True, null=True)
    elo_rating = models.FloatField(default=1200, editable=False)
    match_data = models.JSONField(blank=True, null=True, default=dict)

    def set_rank_based_on_elo(self):
        """
        Updates the clan's rank based on its Elo rating.
        The rank is determined by predefined thresholds.
        """
        if self.elo_rating < 1200:
            self.ranking = 'bronze'
        elif self.elo_rating < 1400:
            self.ranking = 'silver'
        elif self.elo_rating < 1600:
            self.ranking = 'gold'
        elif self.elo_rating < 1800:
            self.ranking = 'platinum'
        elif self.elo_rating < 2000:
            self.ranking = 'diamond'
        elif self.elo_rating < 2200:
            self.ranking = 'master'
        elif self.elo_rating < 2400:
            self.ranking = 'grandmaster'
        elif self.elo_rating < 2600:
            self.ranking = 'champion'
        else:
            self.ranking = 'invincible'

        self.save()
  
    def get_json_file_path(self):
        """
        Returns the file path for storing match data in a JSON file.
        The file is stored in a directory named 'match_data' within the media root.
        """
        directory = os.path.join(settings.MEDIA_ROOT, 'match_data')
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, f'clan_match_data_{self.pk}.json')

    def save_match_data_to_file(self):
        """
        Saves the match data to a JSON file if it exists.
        This is useful for backing up match data externally.
        """
        if not self.match_data:  
            return

        file_path = self.get_json_file_path()
        with open(file_path, 'w') as json_file:
            json.dump(self.match_data, json_file, indent=4)

    def load_match_data_from_file(self):
        """
        Loads match data from the JSON file if it exists.
        Returns the match data as a dictionary or an empty dictionary if the file is empty or invalid.
        """
        file_path = self.get_json_file_path()
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as json_file:
                try:
                    return json.load(json_file)
                except json.JSONDecodeError:
                    return {}
        return {}

    def delete(self, *args, **kwargs):
        """
        Deletes the JSON file associated with the clan's match data when the ClanStats instance is deleted.
        """
        file_path = self.get_json_file_path()
        if os.path.exists(file_path):
            os.remove(file_path)
        super().delete(*args, **kwargs)