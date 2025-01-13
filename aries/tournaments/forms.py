# forms.py
from django import forms
from clubs.models import Clans
from .models import ClanMatch, IndiMatch, ClanTournament, IndiTournament

class ClanMatchScoreForm(forms.ModelForm):
    match_data = forms.JSONField(required=False)

    class Meta:
        model = ClanMatch
        fields = ['match_data']  # Include only the fields you want to update

class IndiMatchScoreForm(forms.ModelForm):
    class Meta:
        model = IndiMatch
        fields = ['player_1_score', 'player_2_score']

class ClanTournamentForm(forms.ModelForm):
    match_data = forms.JSONField(required=False)

    class Meta:
        model = ClanMatch
        fields = ['match_data']

class IndiTournamentForm(forms.ModelForm):
    class Meta:
        model = IndiTournament
        fields = ['name', 'start_date', 'end_date', 'description', 'players']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }



    
