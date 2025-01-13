# forms.py
from django import forms
from clubs.models import Clans
from .models import ClanMatch, IndiMatch, ClanTournament, IndiTournament

class ClanMatchScoreForm(forms.ModelForm):
    class Meta:
        model = ClanMatch
        fields = ['team_1_score', 'team_2_score']

class IndiMatchScoreForm(forms.ModelForm):
    class Meta:
        model = IndiMatch
        fields = ['player_1_score', 'player_2_score']

class ClanTournamentForm(forms.ModelForm):
    class Meta:
        model = ClanTournament
        fields = ['name', 'start_date', 'end_date', 'description', 'teams']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            # Example of filtering the teams to show only active teams or based on some other condition
            self.fields['teams'].queryset = Clans.objects.filter(is_active=True)  # Adjust as per your conditionn

class IndiTournamentForm(forms.ModelForm):
    class Meta:
        model = IndiTournament
        fields = ['name', 'start_date', 'end_date', 'description', 'players']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }