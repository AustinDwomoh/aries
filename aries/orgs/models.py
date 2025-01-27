from django.db import models
from django.contrib.auth.hashers import make_password, check_password


# Create your models here.
class Organization(models.Model):
    """
    Represents an organization (or clan) in the system.
    This model stores details about the organization, including its name, email, password, and other metadata.
    """

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
        """
        Hashes and stores the provided password.
        
        Args:
            raw_password (str): The plain-text password to hash and store.
        """
        self.password = make_password(raw_password)  # Hash the password
        self.save()  # Save the updated password to the database

    def check_password(self, raw_password):
        """
        Checks if the provided password matches the stored hashed password.
        
        Args:
            raw_password (str): The plain-text password to check.
        
        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password(raw_password, self.password) 
    def __str__(self):
        return f"{self.name}"