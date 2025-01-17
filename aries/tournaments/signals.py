from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from itertools import combinations
from .models import ClanTournament, IndiTournament
import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete, sender=ClanTournament)
def delete_json_file(sender, instance, **kwargs):
    file_path = instance.get_json_file_path()
    if os.path.exists(file_path):
        os.remove(file_path)


@receiver(pre_delete, sender=IndiTournament)
def delete_json_file(sender, instance, **kwargs):
    file_path = instance.get_json_file_path()  #
    if os.path.exists(file_path):
        os.remove(file_path)
        