from django.db import models
from django.contrib.auth.hashers import make_password, check_password


# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=255)
    short_hand = models.CharField(max_length=10,null=True)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    org_description = models.TextField()
    org_logo = models.ImageField(default="areis-1.png",upload_to='org_logos')
    org_profile_pic = models.ImageField(default="areis-2.jpg",upload_to='org_profile')
    org_website = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    primary_game = models.CharField(max_length=255, blank=True, null=True) #which games they mainly play
    other_games = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=50)  
    social_links = models.JSONField(blank=True, null=True)
    
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
        return f"{self.name}"