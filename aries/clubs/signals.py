from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Clans,ClanStats
@receiver(post_save,sender = Clans)
def create_profile(sender, instance, created, **kwargs):
    if created:
        clanStats = ClanStats.objects.create(clan=instance)
        clanStats.save()