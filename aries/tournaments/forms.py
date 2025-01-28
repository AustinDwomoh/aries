# forms.py
from django import forms
from clubs.models import Clans
from .models import  ClanTournament, IndiTournament,Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class MatchResultForm(forms.Form):
    """
    Form for submitting match results.
    """
    team_a_goals = forms.IntegerField(
        label="Team A Goals", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': 1})
    )
    team_b_goals = forms.IntegerField(
        label="Team B Goals", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': 1})
    )

#class ClanMacthfOrm(forms.Form):


class IndiTournamentForm(forms.ModelForm):
    """
    Form for creating or updating an individual tournament.
    """
    class Meta:
        model = IndiTournament
        fields = ['name', 'description', 'players', 'tour_type','logo']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Match Name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Match Description'}),
            'tour_type': forms.Select(),
            
        }
    players = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select2'}))

class ClanTournamentForm(forms.ModelForm):
    """
    Form for creating or updating a clan tournament.
    """
    class Meta:
        
        model = ClanTournament
        fields = ['name', 'description', 'teams', 'tour_type','logo']

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Match Name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Match Description'}),
            'tour_type': forms.Select(),
            
        }
    teams = forms.ModelMultipleChoiceField(queryset=Clans.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select2'}))

   


    
