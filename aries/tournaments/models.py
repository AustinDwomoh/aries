from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from clans.models import Clans
from users.models import Profile
from .tourmanager import TourManager
import os,json
from PIL import Image

# Create your models here.
class ClanTournament(models.Model):
    """Clan tournamnet model"""
    TOUR_CHOICES = [('league', 'League'),('cup', 'Cup'),('groups_knockout', 'Groups + Knockout')]
    PLAYER_MODE_CHOICES = [('fixed', 'Fixed'), ('dynamic', 'Dynamic')]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Clans, related_name="clans")
    player_mode = models.CharField(max_length=10,choices=PLAYER_MODE_CHOICES,default='dynamic',help_text="Whether clans can change players mid-tournament")
    home_or_away = models.BooleanField(
        verbose_name="Home or Away",
        default=False,
        help_text="Select if this tournament is played home/away format.",
    )
    logo = models.ImageField(default="tours-defualt.jpg", upload_to='tour_logos')
    tour_type = models.CharField(max_length=100, choices=TOUR_CHOICES)
    

    
    def get_json_file_path(self):
        """Return the file path for the JSON data."""
        # Use a directory  'tournament_data' in the media root
        directory = os.path.join(settings.MEDIA_ROOT, 'tournament_data')
        os.makedirs(directory, exist_ok=True)  # Ensure the directory exists
        return os.path.join(directory, f'tournament_clan_{self.pk}.json')
    
    
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
        
    def save_match_data_to_file(self,match_data):
        """Save match data to a JSON file."""
        file_path = self.get_json_file_path()
        #self.match_data = self.load_match_data_from_file()
        with open(file_path, 'w') as json_file:
            json.dump(match_data, json_file)

    
    def delete(self, *args, **kwargs):
        """Delete the JSON file when the tournament is deleted."""
        file_path = self.get_json_file_path() 
        
         # Get the path to the JSON file
        if os.path.exists(file_path):  # Check if the file exists
            os.remove(file_path)  # Delete the file
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_team_names(self):
        """Extract team names from the related teams."""
        return [team.clan_name for team in self.teams.all()]

    def toggle_player_mode(self):
        self.player_mode = 'fixed' if self.player_mode == 'dynamic' else 'dynamic'
        self.save()
    
    def create_matches(self):
        team_names = self.get_team_names()
        match_data = self.load_match_data_from_file()
        tour_manager = TourManager(json_data=match_data, teams_names=team_names, tournament_type=self.tour_type,home_or_away=self.home_or_away,tour_name= self.name)
        match_data = tour_manager.create_tournament()
        #RETURNS fix and watch this issues
        self.save_match_data_to_file(match_data)

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
        match_data = self.load_match_data_from_file()
        tour_manager = TourManager(json_data=match_data, teams_names=team_names, tournament_type=self.tour_type,home_or_away=self.home_or_away,tour_name= self.name)
        if self.tour_type == "league":
            match_data = tour_manager.update_league(round_number, match_results)
        elif self.tour_type == "cup":
            match_data = tour_manager.update_knockout(round_number, match_results)
        elif self.tour_type == "groups_knockout":
            if KO:
                match_data = tour_manager.update_ko(round_number,match_results)
            else:
                match_data = tour_manager.update_groups_knockout(round_number,match_results)
        else:
            raise ValueError(f"Invalid tournament type: {self.tour_type}")

        self.save_match_data_to_file(match_data)
        return match_data

    
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_matches()

        img = Image.open(self.logo.path)

        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.logo.path)
        
class ClanTournamentPlayer(models.Model):
    clan = models.ForeignKey(Clans, on_delete=models.CASCADE)
    tournament = models.ForeignKey(ClanTournament, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('clan', 'tournament', 'user')


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
    tour_type = models.CharField(max_length=100, choices=TOUR_CHOICES)
    home_or_away = models.BooleanField(
        verbose_name="Home or Away",
        default=False,
        help_text="Select if this tournament is played home/away format.",
    )
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
        tour_manager = TourManager(json_data=self.match_data, teams_names=team_names,home_or_away=self.home_or_away, tournament_type=self.tour_type,tour_name=self.name)
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

        img = Image.open(self.logo.path)

        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.logo.path)

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
        tour_manager =TourManager(json_data=self.match_data, teams_names=team_names,home_or_away=self.home_or_away, tournament_type=self.tour_type,tour_name=self.name)
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
        return updated_data
    
 

