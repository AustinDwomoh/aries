from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from itertools import combinations
from .models import ClanTournament, IndiTournament
import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete, sender=ClanTournament)
def delete_json_file(sender, instance, **kwargs):
    file_path = instance.get_json_file_path()  # Get the file path
    print(f"Signal triggered. File path: {file_path}")  # Debugging
    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted via signal.")
    else:
        print("File not found via signal.")


""" @receiver(m2m_changed, sender=ClanTournament.teams.through)
def create_clan_matches(sender, instance, action, **kwargs):
  
    if action == "post_add":
        teams = list(instance.teams.all())
        for team_1, team_2 in combinations(teams, 2):
            if not ClanMatch.objects.filter(
                tournament=instance, team_1=team_1, team_2=team_2
            ).exists():
                ClanMatch.objects.create(
                    tournament=instance,
                    team_1=team_1,
                    team_2=team_2,
                )

@receiver(m2m_changed, sender=IndiTournament.players.through)
def create_indi_matches(sender, instance, action, **kwargs):
    if action == "post_add": 
        players = list(instance.players.all()) 
        for player_1, player_2 in combinations(players, 2):
            if not IndiMatch.objects.filter(
                tournament=instance,
                player_1=player_1,
                player_2=player_2,
            ).exists():
                IndiMatch.objects.create(
                    tournament=instance,
                    player_1=player_1,
                    player_2=player_2,
                )

 """