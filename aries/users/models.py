from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from clans.models import Clans  
import os,json
from PIL import Image

class Profile(models.Model):
    """
    Profile model to extend Django's built-in User model.
    Each user has a single profile with optional clan membership, social links, 
    a profile picture, and a role within a clan.
    """
    ROLE_CHOICES = [('admin', 'Admin'),('captain', 'Captain'),('member', 'Member'),]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clan = models.ForeignKey(Clans, null=True, blank=True, on_delete=models.SET_NULL, related_name="members") 
    profile_picture = models.ImageField(default="default.jpg",upload_to='profile_pics')
    role = models.CharField(max_length=100,choices=ROLE_CHOICES, blank=True, null=True)
    is_organizer =  models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True, null=True,unique=True)
    is_verified = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f'{self.user.username}'
    
    def save(self,*args, **kwargs): 
        super().save(*args, **kwargs)
        img = Image.open(self.profile_picture.path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
        img.save(self.profile_picture.path)  

class PlayerStats(models.Model):
    """ PlayerStats model to extend Django's built-in User model."""
    user_profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='stats')
    achievements = models.JSONField(blank=True, null=True)
    RANK_CHOICES = [('rookie', 'Rookie'),('prodigy', 'Prodigy'),('veteran', 'Veteran'),('legend', 'Legend'),('superstar', 'Superstar'),('elite', 'Elite'),('mvp', 'MVP'),('world_class', 'World-Class'),]
    rank = models.CharField(max_length=20,choices=RANK_CHOICES,default="Unranked",null=True,editable=False)
    total_matches = models.IntegerField(default=0)
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
        ranking_thresholds = [
            (1200, 'bronze'),
            (1400, 'silver'),
            (1600, 'gold'),
            (1800, 'platinum'),
            (2000, 'diamond'),
            (2200, 'master'),
            (2400, 'grandmaster'),
            (2600, 'champion'),
        ]
        self.rank = 'invincible'

        for threshold, rank in ranking_thresholds:
            if self.elo_rating < threshold:
                self.rank = rank
                break

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

class SocialLink(models.Model):
    SOCIAL_CHOICES = [
        ('discord', 'Discord'),
    ('whatsapp', 'WhatsApp'),
    ('x', 'X / Twitter'),
    ('instagram', 'Instagram'),
    ('tiktok', 'TikTok'),
    ('youtube', 'YouTube'),
    ('twitch', 'Twitch'),
    ('website', 'Website'),
    ('other', 'Other'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='social_links')
    link_type = models.CharField(max_length=20, choices=SOCIAL_CHOICES)
    url = models.URLField(max_length=500)
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which this link should appear")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "link_type"]
        unique_together = ("profile", "link_type")

    def __str__(self):
        return f"{self.get_link_type_display()} - {self.url}"

    def clean(self):
        # Auto-prepend https:// if missing
        if self.url and not self.url.startswith(("http://", "https://")):
            self.url = "https://" + self.url
