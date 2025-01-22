from django.db import models
from django.contrib.auth.models import User
from clubs.models import Clans  

class Profile(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'),('captain', 'Captain'),('member', 'Member'),]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clan = models.ForeignKey(Clans,on_delete=models.CASCADE, null=True, blank=True, related_name="members")
    social_links = models.JSONField(blank=True, null=True) 
    profile_picture = models.ImageField(default="default.jpg",upload_to='profile_pics')
    role = models.CharField(max_length=100,choices=ROLE_CHOICES, blank=True, null=True)
    

    def __str__(self):
        return f'{self.user.username}' 
   


class PlayerStats(models.Model):
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


""" from django.contrib.auth.models import Permission

def assign_permissions(user_profile):
    user = user_profile.user
    if user_profile.role == 'admin':
        user.is_staff = True
        user.is_superuser = True
        user.user_permissions.set(Permission.objects.all())
    elif user_profile.role == 'captain':
        user.is_staff = True
        user.is_superuser = False
        user.user_permissions.set(Permission.objects.filter(codename__in=[
            'add_team_member', 'change_team_details'
        ]))
    elif user_profile.role == 'member':
        user.is_staff = False
        user.is_superuser = False
        user.user_permissions.clear()
    user.save()
 """