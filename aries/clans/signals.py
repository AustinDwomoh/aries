from django.db.models.signals import post_save      
from django.dispatch import receiver      
from .models import Clans, ClanStats  

@receiver(post_save, sender=Clans)  # Register the signal receiver for the Clans model
def create_profile(sender, instance, created, **kwargs):
    """
    Signal receiver function that automatically creates a ClanStats instance
    whenever a new Clans instance is created.

    Args:
        sender (Clans): The model class that sent the signal (Clans in this case).
        instance (Clans): The actual instance of the Clans model that was saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments passed by the signal.
    """
    if created:
        # Create a new ClanStats instance linked to the newly created Clans instance
        clanStats = ClanStats.objects.create(clan=instance)
        clanStats.save()  # Save the ClanStats instance to the database