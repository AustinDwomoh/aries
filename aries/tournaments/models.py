from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from clans.models import Clans
from users.models import Profile
from .tourmanager import TourManager
import os,json
from PIL import Image
from scripts.error_handle import ErrorHandler

# Create your models here.
class ClanTournament(models.Model):
    """
    Represents a clan-based tournament in the system.
    Stores tournament metadata (name, description, format, teams, etc.), manages match schedules/results via JSON files, and handles related file cleanup.
    """
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
        """Returns the absolute path to the JSON file storing match data for this tournament."""
        try:
            directory = os.path.join(settings.MEDIA_ROOT, 'tournament_data')
            os.makedirs(directory, exist_ok=True)  
            return os.path.join(directory, f'tournament_clan_{self.pk}.json')
        except Exception as e:
            ErrorHandler().handle(e,context='Json for clan tournament')
            return RuntimeError("Failed to get JSON file path for clan tournament.")
    
    def load_match_data_from_file(self):
        """
        Loads match data from the JSON file.

        Returns:
            A dictionary containing the match data, or an empty dict if file doesnt exist or is invalid."""
        try:
            file_path = self.get_json_file_path()
            if not file_path:
                return {}

            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, 'r') as json_file:
                    try:
                        return json.load(json_file)
                    except json.JSONDecodeError as e:
                        ErrorHandler().handle(e, context='Invalid JSON in clan match file')
        except Exception as e:
            ErrorHandler().handle(e, context='Loading match data from file')

        return {}
        
    def save_match_data_to_file(self):
        """
        Saves the provided match data to the tournament's JSON file.

        Args:
            match_data (dict): Dictionary containing tournament matches and related data.
        """
        try:
            file_path = self.get_json_file_path()
            #self.match_data = self.load_match_data_from_file()
            with open(file_path, 'w') as json_file:
                json.dump(self.match_data, json_file)
        except Exception as e:
            ErrorHandler().handle(e,context='Save Fail for tour data')

    def delete(self, *args, **kwargs):
        """
        Purpose: Removes the JSON data file when the tournament object is deleted.

        Extra: Calls super().delete() to actually remove the database entry.
        """
        try:
            file_path = self.get_json_file_path()
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            ErrorHandler().handle(e, context=f"Error deleting JSON file for tournament {self.name}")
        finally:
            super().delete(*args, **kwargs)


    def __str__(self):
        return self.name
    
    def get_team_names(self):
        """Returns a list of clan names for the participating teams"""
        return [team.clan_name for team in self.teams.all()]

    def toggle_player_mode(self):
        """Switches player_mode between dynamic and fixed and saves the change"""
        try:
            self.player_mode = 'fixed' if self.player_mode == 'dynamic' else 'dynamic'
            self.save()
        except Exception as e:
            ErrorHandler().handle(e,context='Changing tour mode')
    
    def create_matches(self):
        """
        Generates the match schedule for the clan tournament using TourManager.

        Fails if no teams are registered or if matches already exist.
        """
        try:
            team_names = self.get_team_names()
            self.match_data = self.load_match_data_from_file()
           
            tour_manager = TourManager(
                json_data=self.match_data,
                teams_names=team_names,
                tournament_type=self.tour_type,
                home_or_away=self.home_or_away,
                tour_name=self.name
            )
            self.match_data = tour_manager.create_tournament()
            print(self.match_data)
        
            self.save_match_data_to_file()
        except Exception as e:
            ErrorHandler().handle(e, context="Creating Clan tournament matches")


    def update_tour(self, round_number, match_results, KO=None):
        """
        Updates the match results for the given round, handling the specific tournament type (league, knockout, or groups + knockout).

        Args:
            round_number: The round being updated.
            match_results: List of match results.
            KO: Knockout stage ID (for groups_knockout format).

        Returns:
            Updated match data dict.
        """
        try:
            team_names = self.get_team_names()
            match_data = self.load_match_data_from_file()
            tour_manager = TourManager(json_data=match_data, teams_names=team_names, tournament_type=self.tour_type,home_or_away=self.home_or_away,tour_name= self.name)
            if self.tour_type == "league":
                match_data = tour_manager.update_league(round_number, match_results)
            elif self.tour_type == "cup":
                match_data = tour_manager.update_knockout(round_number, match_results)
            elif self.tour_type == "groups_knockout":
                if KO:
                    match_data = tour_manager.update_knockout_stage(round_number,match_results)
                else:
                    match_data = tour_manager.update_groups_stages(round_number,match_results)
            else:
                raise ValueError(f"Invalid tournament type: {self.tour_type}")

            self.save_match_data_to_file(match_data)
            
        except Exception as e:
            ErrorHandler().handle(e,context='Update macthes error')
            if settings.DEBUG:
                raise
        finally:
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
    Represents a individual-based tournament in the system.
    Stores tournament metadata (name, description, format, teams, etc.), manages match schedules/results via JSON files, and handles related file cleanup.
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
        """Returns the absolute path to the JSON file storing match data for this tournament."""
        try:
            directory = os.path.join(settings.MEDIA_ROOT, 'tournament_data')
            os.makedirs(directory, exist_ok=True)  
        except Exception as e:
            ErrorHandler().handle(e,context='Json for Indi tournament')
            return RuntimeError("Failed to get JSON file path for clan tournament.")
        finally:
            return os.path.join(directory, f'tournament_indi_{self.pk}.json')

    def save_match_data_to_file(self):
        """
        Saves the provided match data to the tournament's JSON file.
        """
        try:
            file_path = self.get_json_file_path()
            with open(file_path, 'w') as json_file:
                json.dump(self.match_data, json_file)
        except Exception as e:
            ErrorHandler().handle(e,context='Save Fail for tour data')
    
    def load_match_data_from_file(self):
        """
        Loads match data from the JSON file.

        Returns:
            A dictionary containing the match data, or an empty dict if file doesnt exist or is invalid."""
        try:
            file_path = self.get_json_file_path()
            if not file_path:
                return {}

            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, 'r') as json_file:
                    try:
                        return json.load(json_file)
                    except json.JSONDecodeError as e:
                        ErrorHandler().handle(e, context='Invalid JSON in clan match file')
        except Exception as e:
            ErrorHandler().handle(e, context='Loading match data from file')

        return {}
    
    def delete(self, *args, **kwargs):
        """
        Purpose: Removes the JSON data file when the tournament object is deleted.

        Extra: Calls super().delete() to actually remove the database entry.
        """
        try:
            file_path = self.get_json_file_path()
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            ErrorHandler().handle(e, context=f"Error deleting JSON file for tournament {self.name}")
        finally:
            super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    def create_matches(self):
        """
        Generates the match schedule for the individual tournament using TourManager.

        Fails if no teams are registered or if matches already exist.
        """
        try:
            team_names = self.get_team_names()
            self.match_data = self.load_match_data_from_file()
            tour_manager = TourManager(json_data=self.match_data, teams_names=team_names,home_or_away=self.home_or_away, tournament_type=self.tour_type,tour_name=self.name)
            matches = tour_manager.create_tournament()
            self.match_data =  matches  
            self.save_match_data_to_file()
        except Exception as e:
            ErrorHandler().handle(e, context="Creating indi tournament matches")

            
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
        Updates the match results for the given round, handling the specific tournament type (league, knockout, or groups + knockout).

        Args:
            round_number: The round being updated.
            match_results: List of match results.
            KO: Knockout stage ID (for groups_knockout format).

        Returns:
            Updated match data dict.
        """
        try:
            team_names = self.get_team_names()
            self.match_data = self.load_match_data_from_file()
            tour_manager =TourManager(json_data=self.match_data, teams_names=team_names,home_or_away=self.home_or_away, tournament_type=self.tour_type,tour_name=self.name)
            if self.tour_type == "league":
                updated_data = tour_manager.update_league(round_number, match_results)
            elif self.tour_type == "cup":
                updated_data = tour_manager.update_knockout(round_number, match_results)
            elif self.tour_type == "groups_knockout":
                if KO:
                    updated_data = tour_manager.update_knockout_stage(round_number,match_results)
                else:
                    updated_data = tour_manager.update_groups_stages(round_number,match_results)
            else:
                raise ValueError(f"Invalid tournament type: {self.tour_type}")
            self.save_match_data_to_file()
            
        except Exception as e:
            ErrorHandler().handle(e,context='Update macthes error')
            if settings.DEBUG:
                raise
        finally:
            return updated_data
 

