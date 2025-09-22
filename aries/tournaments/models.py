from django.db import models
from django.contrib.auth.models import User
from organizations.models import Organization
from clans.models import Clan
from .tourmanager import TourManager
import os
import json
from PIL import Image
from scripts.error_handle import ErrorHandler

# Create your models here.
class Tournament(models.Model):
    """
    Tournament model that supports both individual and clan-based tournaments.
    Individual tournaments: Users participate directly
    Clan tournaments: Clans participate as teams
    Organizations are the organizers, not participants
    """
    TOUR_CHOICES = [('league', 'League'),('cup', 'Cup'),('groups_knockout', 'Groups + Knockout')]
    TOURNAMENT_TYPE_CHOICES = [
        ('individual', 'Individual Tournament'),
        ('clan', 'Clan Tournament'),
    ]
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    organizer = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='organized_tournaments')
    tournament_type = models.CharField(max_length=20, choices=TOURNAMENT_TYPE_CHOICES, default='individual')
    tour_format = models.CharField(max_length=100, choices=TOUR_CHOICES, default='league')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    # Tournament settings
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(blank=True, null=True)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Format settings
    home_or_away = models.BooleanField(
        verbose_name="Home or Away",
        default=False,
        help_text="Select if this tournament is played home/away format.",
    )
    
    # Media
    logo = models.ImageField(default="tours-default.jpg", upload_to='tour_logos')
    
    # Match data stored in JSON
    match_data = models.JSONField(blank=True, null=True, default=dict)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Tournament"
        verbose_name_plural = "Tournaments"
    
    def __str__(self):
        return self.name
    
    def get_json_file_path(self):
        """Returns the absolute path to the JSON file storing match data for this tournament."""
        try:
            directory = os.path.join(settings.MEDIA_ROOT, 'tournament_data')
            os.makedirs(directory, exist_ok=True)  
            return os.path.join(directory, f'tournament_{self.pk}.json')
        except Exception as e:
            ErrorHandler().handle(e, context='Json for tournament')
            return None
    
    def load_match_data_from_file(self):
        """Loads match data from the JSON file."""
        try:
            file_path = self.get_json_file_path()
            if not file_path:
                return {}

            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, 'r') as json_file:
                    try:
                        return json.load(json_file)
                    except json.JSONDecodeError as e:
                        ErrorHandler().handle(e, context='Invalid JSON in tournament file')
        except Exception as e:
            ErrorHandler().handle(e, context='Loading match data from file')

        return {}
    
    def save_match_data_to_file(self):
        """Saves the match data to the tournament's JSON file."""
        try:
            file_path = self.get_json_file_path()
            if file_path:
                with open(file_path, 'w') as json_file:
                    json.dump(self.match_data, json_file, indent=4)
        except Exception as e:
            ErrorHandler().handle(e, context='Save Fail for tournament data')
    
    def delete(self, *args, **kwargs):
        """Removes the JSON data file when the tournament object is deleted."""
        try:
            file_path = self.get_json_file_path()
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            ErrorHandler().handle(e, context=f"Error deleting JSON file for tournament {self.name}")
        finally:
            super().delete(*args, **kwargs)
    
    def get_participants(self):
        """Get all participants in this tournament."""
        if self.tournament_type == 'individual':
            return [participant.user for participant in self.participants.all()]
        else:  # clan tournament
            return [participant.clan for participant in self.participants.all()]
    
    def get_participant_names(self):
        """Get participant names for tournament management."""
        if self.tournament_type == 'individual':
            return [participant.user.username for participant in self.participants.all()]
        else:  # clan tournament
            return [participant.clan.name for participant in self.participants.all()]
    
    def create_matches(self):
        """Generates the match schedule for the tournament using TourManager."""
        try:
            participant_names = self.get_participant_names()
            if not participant_names:
                return
            
            self.match_data = self.load_match_data_from_file()
            
            tour_manager = TourManager(
                json_data=self.match_data,
                teams_names=participant_names,
                tournament_type=self.tour_format,
                home_or_away=self.home_or_away,
                tour_name=self.name
            )
            self.match_data = tour_manager.create_tournament()
            self.save_match_data_to_file()
        except Exception as e:
            ErrorHandler().handle(e, context="Creating tournament matches")
    
    def update_tournament(self, round_number, match_results, KO=None):
        """Updates the match results for the given round."""
        try:
            participant_names = self.get_participant_names()
            match_data = self.load_match_data_from_file()
            
            tour_manager = TourManager(
                json_data=match_data, 
                teams_names=participant_names, 
                tournament_type=self.tour_format,
                home_or_away=self.home_or_away,
                tour_name=self.name
            )
            
            if self.tour_format == "league":
                match_data = tour_manager.update_league(round_number, match_results)
            elif self.tour_format == "cup":
                match_data = tour_manager.update_knockout(round_number, match_results)
            elif self.tour_format == "groups_knockout":
                if KO:
                    match_data = tour_manager.update_knockout_stage(round_number, match_results)
                else:
                    match_data = tour_manager.update_groups_stages(round_number, match_results)
            else:
                raise ValueError(f"Invalid tournament format: {self.tour_format}")

            self.match_data = match_data
            self.save_match_data_to_file()
            
        except Exception as e:
            ErrorHandler().handle(e, context='Update matches error')
            if settings.DEBUG:
                raise
        finally:
            return self.match_data
    
    def save(self, *args, **kwargs):
        """Save the tournament and create matches if participants exist."""
        super().save(*args, **kwargs)
        
        # Resize logo if needed
        if self.logo:
            try:
                img = Image.open(self.logo.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.logo.path)
            except Exception as e:
                ErrorHandler().handle(e, context=f"Error resizing tournament logo for {self.name}")


class TournamentParticipant(models.Model):
    """
    Represents a participant in a tournament.
    Can be either an individual user or a clan.
    """
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('eliminated', 'Eliminated'),
        ('withdrawn', 'Withdrawn'),
    ], default='active')
    
    class Meta:
        unique_together = [
            ('tournament', 'user'),
            ('tournament', 'clan'),
        ]
        verbose_name = "Tournament Participant"
        verbose_name_plural = "Tournament Participants"
    
    def clean(self):
        """Ensure either user or clan is set, but not both."""
        from django.core.exceptions import ValidationError
        
        if not self.user and not self.clan:
            raise ValidationError("Either user or clan must be specified.")
        
        if self.user and self.clan:
            raise ValidationError("Cannot specify both user and clan.")
    
    def __str__(self):
        if self.user:
            return f"{self.user.username} in {self.tournament.name}"
        else:
            return f"{self.clan.name} in {self.tournament.name}"


class Match(models.Model):
    """
    Represents a match in a tournament.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    round_number = models.PositiveIntegerField()
    home_participant = models.ForeignKey(TournamentParticipant, on_delete=models.CASCADE, related_name='home_matches')
    away_participant = models.ForeignKey(TournamentParticipant, on_delete=models.CASCADE, related_name='away_matches')
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    scheduled_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    is_knockout = models.BooleanField(default=False)
    knockout_stage = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['round_number', 'scheduled_at']
        verbose_name = "Match"
        verbose_name_plural = "Matches"
    
    def __str__(self):
        home_name = self.home_participant.user.username if self.home_participant.user else self.home_participant.organization.name
        away_name = self.away_participant.user.username if self.away_participant.user else self.away_participant.organization.name
        return f"{home_name} vs {away_name} - Round {self.round_number}"
    
    def get_winner(self):
        """Get the winner of the match."""
        if self.status != 'completed' or self.home_score is None or self.away_score is None:
            return None
        
        if self.home_score > self.away_score:
            return self.home_participant
        elif self.away_score > self.home_score:
            return self.away_participant
        else:
            return None  # Draw
