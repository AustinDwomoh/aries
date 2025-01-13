from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from itertools import combinations
from .models import ClanTournament, IndiTournament, ClanMatch, IndiMatch


@receiver(m2m_changed, sender=ClanTournament.teams.through)
def create_clan_matches(sender, instance, action, **kwargs):
    """
    Automatically create ClanMatch objects when teams are added to a tournament.
    """
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
    """
    Automatically create matches when players are added to an IndiTournament.
    """
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

