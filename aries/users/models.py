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
        return f'{self.user.username} {self.role}' 
   


class PlayerStats(models.Model):
    user_profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='stats')
    achievements = models.JSONField(blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True, editable=False)
    games_played = models.IntegerField(default=0)
    win_rate = models.FloatField(default=0.0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    total_draws = models.IntegerField(default=0)
    gd = models.IntegerField(default=0)
    gf = models.IntegerField(default=0)
    ga = models.IntegerField(default=0)
    


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