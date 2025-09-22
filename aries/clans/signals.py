from django.db.models.signals import post_save      
from django.dispatch import receiver      
from .models import Clan, ClanStats  

@receiver(post_save, sender=Clan)  # Register the signal receiver for the Clan model
def create_profile(sender, instance, created, **kwargs):
    """
    Signal receiver function that automatically creates a ClanStats instance
    whenever a new Clan instance is created.

    Args:
        sender (Clan): The model class that sent the signal (Clan in this case).
        instance (Clan): The actual instance of the Clan model that was saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments passed by the signal.
    """
    if created:
        clanStats = ClanStats.objects.create(clan=instance)
        clanStats.save() 