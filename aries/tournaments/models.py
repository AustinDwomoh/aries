from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from clubs.models import Clans,ClanStats
from users.models import Profile,PlayerStats
from .tourmanager import TourManager
import os 
import json

# Create your models here.
class ClanTournament(models.Model):
    """Clan tournamnet model"""
    TOUR_CHOICES = [('league', 'League'),('cup', 'Cup'),('groups_knockout', 'Groups + Knockout')]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Clans, related_name="clans")  # Many-to-many relation with Clans
    logo = models.ImageField(default="tours-defualt.jpg", upload_to='tour_logos')
    tour_type = models.CharField(max_length=100, choices=TOUR_CHOICES, blank=True, null=True)
    

    def get_json_file_path(self):
        """Return the file path for the JSON data."""
        # Use a directory  'tournament_data' in the media root
        directory = os.path.join(settings.MEDIA_ROOT, 'tournament_data')
        os.makedirs(directory, exist_ok=True)  # Ensure the directory exists
        return os.path.join(directory, f'tournament_clan_{self.pk}.json')

    def save_match_data_to_file(self):
        """Save match data to a JSON file."""
        file_path = self.get_json_file_path()
        with open(file_path, 'w') as json_file:
            json.dump(self.match_data, json_file)

    def load_match_data_from_file(self):
        """Load match data from the JSON file."""
        file_path = self.get_json_file_path()
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as json_file:
                try:
                    return json.load(json_file)
                except json.JSONDecodeError:
                    # Handle invalid JSON
                    print("Error decoding JSON.")
                    return {}
        else:
            return {}
    
    def delete(self, *args, **kwargs):
        """Delete the JSON file when the tournament is deleted."""
        file_path = self.get_json_file_path()  # Get the path to the JSON file
        if os.path.exists(file_path):  # Check if the file exists
            os.remove(file_path)  # Delete the file
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_team_names(self):
        """Extract team names from the related teams."""
        return [team.clan_name for team in self.teams.all()]

    def create_matches(self):
        team_names = self.get_team_names()
        self.match_data = self.load_match_data_from_file()
        tour_manager = TourManager(self.match_data, team_names, self.tour_type)
        matches = tour_manager.create_tournament()
        self.match_data = matches
        self.save_match_data_to_file()

    def update_tour(self, round_number, match_results, KO=None):
        """
        Update the tournament data based on the type of tournament.

        Args:
            round_number (int): The round number to update.
            match_results (list of dict): Results of matches to update.
            KO (str, optional): The knockout stage identifier for 'groups_knockout' tournaments.

        Returns:
            dict: Updated match data after applying changes.

        Raises:
            ValueError: If the tournament type is invalid.
        """
        team_names = self.get_team_names()
        self.match_data = self.load_match_data_from_file()
        tour_manager = TourManager(self.match_data, team_names, self.tour_type)
        if self.tour_type == "league":
            updated_data = tour_manager.update_league(round_number, match_results)
        elif self.tour_type == "cup":
            updated_data = tour_manager.update_knockout(round_number, match_results)
        elif self.tour_type == "groups_knockout":
            if KO:
                updated_data = tour_manager.update_ko(round_number,match_results)
            else:
                 updated_data = tour_manager.update_groups_knockout(round_number,match_results)
        else:
            raise ValueError(f"Invalid tournament type: {self.tour_type}")
        self.save_match_data_to_file()
        self.update_clan_stats()# stop calling iut here and call it in the tourmanger when all matches are complete so it can update instead of the out of proporition style
        return updated_data

    def update_clan_stats(self):
        """
        Update clan statistics based on the tournament results.
        """
        match_data = self.load_match_data_from_file()

        if self.tour_type == "league" or self.tour_type == "cup":
            table = match_data["table"]
            for team_name, team_data in table.items():
                clan_stat = ClanStats.objects.get(clan__clan_name=team_name)
                clan_stat.gd += team_data["goal_difference"]
                clan_stat.gf += team_data["goals_scored"]
                clan_stat.ga += team_data["goals_conceded"]
                clan_stat.total_matches += team_data["matches_played"]
                clan_stat.wins += team_data["wins"]
                clan_stat.draws += team_data["draws"]
                clan_stat.losses += team_data["losses"]
                win_rate = ((clan_stat.wins + clan_stat.draws/2) / clan_stat.total_matches) * 100 if clan_stat.total_matches > 0 else 0
                clan_stat.win_rate = round(win_rate,3)
                clan_stat.save()
        elif self.tour_type == "groups_knockout": 
            pass 
        self.save_match_data_to_file()
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_matches()


class IndiTournament(models.Model):
    """
    Model representing an individual tournament.
    """
    TOUR_CHOICES = [('league', 'League'),('cup', 'Cup'),('groups_knockout', 'Groups + Knockout')]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    players = models.ManyToManyField(Profile, related_name="players")
    logo = models.ImageField(default="tours-defualt.jpg",upload_to='tour_logos')
    tour_type = models.CharField(max_length=100, choices=TOUR_CHOICES, blank=True, null=True)
    def __str__(self):
        return self.name
    def get_team_names(self):
        """Extract team names from the related teams."""
        return [team.user.username for team in self.players.all()]

    def get_json_file_path(self):
        """Return the file path for the JSON data."""
        # Use a directory named 'tournament_data' in the media root
        directory = os.path.join(settings.MEDIA_ROOT, 'tournament_data')
        os.makedirs(directory, exist_ok=True)  # Ensure the directory exists
        return os.path.join(directory, f'tournament_indi_{self.pk}.json')

    def save_match_data_to_file(self):
        """Save match data to a JSON file."""
        file_path = self.get_json_file_path()
        with open(file_path, 'w') as json_file:
            json.dump(self.match_data, json_file)

    def load_match_data_from_file(self):
        """Load match data from the JSON file."""
        file_path = self.get_json_file_path()
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as json_file:
                try:
                    return json.load(json_file)
                except json.JSONDecodeError:
                    return {}
        else:
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
        """
        Create matches for the indi tournament using the TourManager.
        """
        team_names = [team.user.username for team in self.players.all()]
        self.match_data = self.load_match_data_from_file()
        tour_manager = TourManager(self.match_data, team_names, self.tour_type)
        matches = tour_manager.create_tournament()
        self.match_data =  matches  
        self.save_match_data_to_file()
        
    def save(self, *args, **kwargs):
        """
        Save the tournament and create matches.
        """
        if not hasattr(self, '_saving'):
            self._saving = True  
            super().save(*args, **kwargs)
            self.create_matches()

            super().save(*args, **kwargs)
            del self._saving  
        else:
            super().save(*args, **kwargs)

    def update_tour(self, round_number, match_results, KO=None):
        """
        Update the tournament data based on the type of tournament.

        Args:
            round_number (int): The round number to update.
            match_results (list of dict): Results of matches to update.
            KO (str, optional): The knockout stage identifier for 'groups_knockout' tournaments.

        Returns:
            dict: Updated match data after applying changes.

        Raises:
            ValueError: If the tournament type is invalid.
        """
        team_names = self.get_team_names()
        self.match_data = self.load_match_data_from_file()
        tour_manager = TourManager(self.match_data, team_names, self.tour_type)
        if self.tour_type == "league":
            updated_data = tour_manager.update_league(round_number, match_results)
        elif self.tour_type == "cup":
            updated_data = tour_manager.update_knockout(round_number, match_results)
        elif self.tour_type == "groups_knockout":
            if KO:
                print(KO)
                updated_data = tour_manager.update_ko(round_number,match_results)
            else:
                 updated_data = tour_manager.update_groups_knockout(round_number,match_results)
        else:
            raise ValueError(f"Invalid tournament type: {self.tour_type}")
        self.save_match_data_to_file()
        self.update_indi_stats()
        return updated_data
    
    def update_indi_stats(self):
        #rewrite this to use the match calls for stats update
        """
        Update individual player statistics based on the tournament results.
        """
        match_data = self.load_match_data_from_file()

        if self.tour_type == "league" or self.tour_type == "cup"  :
            table = match_data["table"]
            for team_name, team_data in table.items():
                user = User.objects.get(username=team_name)
                user_stat = user.profile.stats
                user_stat.gd += team_data["goal_difference"]
                user_stat.gf += team_data["goals_scored"]
                user_stat.ga += team_data["goals_conceded"]
                user_stat.games_played += team_data["matches_played"]
                user_stat.total_wins += team_data["wins"]
                user_stat.total_draws += team_data["draws"]
                user_stat.total_losses += team_data["losses"]
                win_rate = ((user_stat.total_wins + user_stat.total_draws/2) / user_stat.games_played) * 100 if user_stat.games_played > 0 else 0
                user_stat.win_rate = round(win_rate,3)
                user_stat.save()
        else:
            table = match_data["knock_outs"]["table"]

