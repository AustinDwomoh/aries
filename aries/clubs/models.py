from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User



# Create your models here.



class Clans(models.Model):
    # Basic Information
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
    clan = models.OneToOneField(Clans, on_delete=models.CASCADE,related_name='stat')
    total_matches = models.IntegerField(default=0, editable=False)
    win_rate = models.FloatField(default=0.0, editable=False)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    ranking = models.IntegerField(blank=True, null=True, editable=False)
    gd = models.IntegerField(default=0)
    gf = models.IntegerField(default=0)
    ga = models.IntegerField(default=0)
    average_team_score = models.FloatField(default=0.0, editable=False)
    achievements = models.JSONField(blank=True, null=True)
    leaderboard_position = models.IntegerField(blank=True, null=True)
    """ from django.db import models
from django_countries.fields import CountryField

class MyModel(models.Model):
    country = CountryField(blank_label='(select country)', default='US')  # You can set a default country here if you like

    def __str__(self):
        return str(self.country) """