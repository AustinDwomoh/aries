from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile,PlayerStats

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    This function is triggered after a User instance is saved.
    It creates a Profile associated with the newly created User.
    """
    if created:  
        profile = Profile.objects.create(user=instance)  
        profile.save()  


@receiver(post_save, sender=Profile)
def create_profile_stats(sender, instance, created, **kwargs):
    """
    This function is triggered after a Profile instance is saved.
    It creates PlayerStats associated with the newly created Profile.
    """
    if created:  
        profile = PlayerStats.objects.create(user_profile=instance)  
        profile.save()