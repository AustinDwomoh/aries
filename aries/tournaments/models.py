from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from clubs.models import Clans
from users.models import Profile
from django.utils import timezone
from django.db.models import Q
from .tourmanager import TourManager
import os 
import json

# Create your models here.
class ClanTournament(models.Model):
    TOUR_CHOICES = [
        ('league', 'League'),
        ('cup', 'Cup'),
        ('league_knockout', 'League + Knockout'),
        ('groups_knockout', 'Groups + Knockout'),
    ]
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Clans, related_name="ClanMatch")  # Many-to-many relation with Clans
    logo = models.ImageField(default="tours-defualt.jpg", upload_to='tour_logos')
    tour_type = models.CharField(max_length=100, choices=TOUR_CHOICES, blank=True, null=True)
    

    def get_json_file_path(self):
        """Return the file path for the JSON data."""
        # Use a directory named 'tournament_data' in the media root
        directory = os.path.join(settings.MEDIA_ROOT, 'tournament_data')
        os.makedirs(directory, exist_ok=True)  # Ensure the directory exists
        return os.path.join(directory, f'tournament_{self.pk}.json')

    def save_match_data_to_file(self):
        """Save match data to a JSON file."""
        file_path = self.get_json_file_path()
        with open(file_path, 'w') as json_file:
            json.dump(self.match_data, json_file)

    def load_match_data_from_file(self):
        """Load match data from the JSON file."""
        file_path = self.get_json_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                return json.load(json_file)
        return {}
    
    def delete(self, *args, **kwargs):
        """Delete the JSON file when the tournament is deleted."""
        file_path = self.get_json_file_path()  # Get the path to the JSON file
        if os.path.exists(file_path):  # Check if the file exists
            os.remove(file_path)  # Delete the file
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    def create_matches(self):
        # Ensure there are enough teams
        team_names = [team.clan_name for team in self.teams.all()]
        print(self.teams.all())  # Debugging print statement
    
       
        self.match_data = self.load_match_data_from_file()
        # Create matches with a tournament manager
        tour_manager = TourManager(self.match_data, team_names, self.tour_type)
        matches = tour_manager.create_tournament()
        print('in model')
        print(matches)
        self.match_data = {'matches': matches}  # Update match data
        self.save_match_data_to_file()
        print('in model')
        print(matches)  # Store match data

    def save(self, *args, **kwargs):
        if not hasattr(self, '_saving'):
            self._saving = True  
            super().save(*args, **kwargs)
            self.create_matches()

            super().save(*args, **kwargs)
            del self._saving  
        else:
            super().save(*args, **kwargs)

        
    """


    def update_clan_stats(self):
        data = self.match_data
        self.team_1_score = data['team_1']['wins']
        self.team_2_score = data['team_2']['wins']
        if self.team_1_score == self.team_2_score:
            self.is_draw = True
            self.winner = None 
            self.team_2.stat.draws += 1
            self.team_1.stat.draws += 1 
        else:
            self.is_draw = False
            if self.team_1_score > self.team_2_score:
                self.winner = self.team_1.clan
                self.team_1.stat.wins += 1
                self.team_2.stat.losses += 1
            else:
                self.winner = self.team_2.clan
                self.team_2.stat.wins += 1
                self.team_1.stat.losses += 1
        
        self.team_1.stat.total_matches += 1  
        self.team_1.stat.gf +=  data['team_1']['scores']
        self.team_1.stat.ga += data['team_2']['scores']
        self.team_1.stat.save()

        self.team_2.stat.total_matches += 1
        self.team_2.stat.gf = data['team_2']['scores']
        self.team_2.stat.ga =  data['team_1']['scores']
        self.team_2.stat.save()

    def create_match_data(self):
        # Pair players up from both teams (assuming they're ordered in the same way)
        team_1_players = list(self.team_1.members.all())
        team_2_players = list(self.team_2.members.all())
        match_results = {
            "matches":{},
            "team_1": {
                "wins": 0,
                "draws":0,
                "losses":0,
                "scores":0
            },
            "team_2": {
                "wins": 0,
                "draws":0,
                "losses":0,
                "scores":0
            },
            "winner": None,
        }
        match_id = 1  # Start match ID from 1

        for player1, player2 in zip(team_1_players, team_2_players):
            match_results["matches"][match_id] = {
                "player1": {"name": player1.user.username, "goals": 0},
                "player2": {"name": player2.user.username, "goals": 0},
            }
            match_id += 1
        self.match_data = match_results

    def calculate_player_match_result(self):
        match_results = self.match_data
        matches = list(match_results["matches"].values())
        for i in range(len(matches)):
            match = matches[i]
            player1 = match["player1"]
            player2 = match["player2"]
            self.update_player_stats(player1,player2)
            if player1["goals"] > player2["goals"]:
                player_1_wins = 1  
                player_2_wins = 0  
            elif player1["goals"] < player2["goals"]:
                player_1_wins = 0 
                player_2_wins = 1  
            else:
                player_1_wins = 0  
                player_2_wins = 0  
            match_results["team_1"]["wins"] += player_1_wins
            match_results["team_2"]["wins"] += player_2_wins
            match_results["team_1"]["losses"] += player_2_wins
            match_results["team_2"]["losses"] += player_1_wins

            if player1["goals"] == player2["goals"]:
                match_results["team_1"]["draws"] += 1
                match_results["team_2"]["draws"] += 1

            match_results["team_1"]["scores"] += player_1_wins  
            match_results["team_2"]["scores"] += player_2_wins  
        self.match_data = match_results
        self.update_clan_stats()

    def update_player_stats(self,player1,player2):
        p1 = User.objects.get(username=player1['name'])
        p2 = User.objects.get(username=player2['name'])
        if player1['goals'] > player2['goals']:
            p1.stats.total_wins += 1
            p2.stats.total_losses += 1
        elif player1['goals'] < player2['goals']:
            p1.stats.total_wins += 1
            p2.stats.total_losses += 1
        else:
            p1.stats.total_draws += 1
            p2.stats.total_draws += 1
        

        p1.stat.games_played += 1  
        p1.stat.gf +=  player1['goals']
        p1.stat.ga += player2['goals']
        p1.stat.save()

        p2.stat.games_played += 1
        p2.stat.gf = player2['goals']
        p2.stat.ga =  player1['goals']
        p2.stat.save()
 """


class IndiTournament(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    players = models.ManyToManyField(Profile, related_name="IndiMatch")  # Many-to-many relation with Players
    logo = models.ImageField(default="tours-defualt.jpg",upload_to='tour_logos')
    match_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

""" 
    def save(self, *args, **kwargs):
        if self.player_1_score > self.player_2_score:
            self.winner = self.player_1
        elif self.player_2_score > self.player_1_score:
            self.winner = self.player_2
        else:
            self.is_draw = True
            self.winner = None  # Draw match has no winner
        super().save(*args, **kwargs)

        # Update Player stats
        self.update_player_stats()

    def update_player_stats(self):
        for player in [self.player_1, self.player_2]:
            player_stats = player.stats
            matches = IndiMatch.objects.filter(Q(player_1=player) | Q(player_2=player))
            player_stats.games_played = matches.count()
            player_stats.total_wins = matches.filter(winner=player).count()
            player_stats.total_losses = matches.filter(winner__isnull=False).exclude(winner=player).count()
            player_stats.total_draws = matches.filter(is_draw=True).count()
            player_stats.win_rate = (player_stats.total_wins / player_stats.games_played) * 100 if player_stats.games_played > 0 else 0
            player_stats.save()
 """