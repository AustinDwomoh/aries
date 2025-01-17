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
    TOUR_CHOICES = [('league', 'League'),('cup', 'Cup'),('groups_knockout', 'Groups + Knockout')]
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

    def create_matches(self):
        team_names = [team.clan_name for team in self.teams.all()]
        self.match_data = self.load_match_data_from_file()
        tour_manager = TourManager(self.match_data, team_names, self.tour_type)
        matches = tour_manager.create_tournament()
        self.match_data = {'matches': matches}  
        self.save_match_data_to_file()
        
    def save(self, *args, **kwargs):
        if not hasattr(self, '_saving'):
            self._saving = True  
            super().save(*args, **kwargs)
            self.create_matches()

            super().save(*args, **kwargs)
            del self._saving  
        else:
            super().save(*args, **kwargs)


class IndiTournament(models.Model):
    TOUR_CHOICES = [('league', 'League'),('cup', 'Cup'),('groups_knockout', 'Groups + Knockout')]
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    players = models.ManyToManyField(Profile, related_name="IndiMatch")  # Many-to-many relation with Players
    logo = models.ImageField(default="tours-defualt.jpg",upload_to='tour_logos')
    tour_type = models.CharField(max_length=100, choices=TOUR_CHOICES, blank=True, null=True)
    def __str__(self):
        return self.name

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

    def create_matches(self):
        team_names = [team.user.username for team in self.players.all()]
        self.match_data = self.load_match_data_from_file()
        tour_manager = TourManager(self.match_data, team_names, self.tour_type)
        matches = tour_manager.create_tournament()
        self.match_data = {'matches': matches}  
        self.save_match_data_to_file()
        
    def save(self, *args, **kwargs):
        if not hasattr(self, '_saving'):
            self._saving = True  
            super().save(*args, **kwargs)
            self.create_matches()

            super().save(*args, **kwargs)
            del self._saving  
        else:
            super().save(*args, **kwargs)

   