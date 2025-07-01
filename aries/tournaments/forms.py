# forms.py
from django import forms
from clans.models import Clans
from django.contrib.auth.models import User
from .models import  ClanTournament, IndiTournament,Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.contenttypes.models import ContentType
from Home.models import Follow

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



class IndiTournamentForm(forms.ModelForm):
    """
    Form for creating or updating an individual tournament.
    """

    class Meta:
        model = IndiTournament
        fields = ['name', 'description', 'players', 'tour_type','logo','home_or_away']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Match Name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Match Description'}),
            'tour_type': forms.Select(),
            'home_or_away': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            
        }

    
    
    def __init__(self, *args, current_profile=None, **kwargs):
        super().__init__(*args, **kwargs)

        if current_profile:
            profile_type = ContentType.objects.get_for_model(User)

            # Get the list of follower ids
            follower_ids = Follow.objects.filter(
                followed_type=profile_type,
                followed_id=current_profile.id,
                follower_type=profile_type
            ).values_list('follower_id', flat=True)

            self.fields['players'] = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select2'}))
            #.filter(id__in=follower_ids)
        else:
            # Fallback: No followers, empty queryset for 'players'
            self.fields['players'] = forms.ModelMultipleChoiceField(queryset=Profile.objects.none(), widget=forms.SelectMultiple(attrs={'class': 'select2'}))
    #

class ClanTournamentForm(forms.ModelForm):
    """
    Form for creating or updating a clan tournament.
    """
    class Meta:
        model = ClanTournament
        fields = ['name', 'description', 'teams', 'tour_type', 'logo', 'home_or_away']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Match Name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Match Description'}),
            'tour_type': forms.Select(),
            'home_or_away': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        }
    def __init__(self, *args, current_profile=None, **kwargs):
        super().__init__(*args, **kwargs)

        if current_profile:
            profile_type = ContentType.objects.get_for_model(Clans)

            # Get the list of follower ids
            follower_ids = Follow.objects.filter(
                followed_type=profile_type,
                followed_id=current_profile.id,
                follower_type=profile_type
            ).values_list('follower_id', flat=True)

            self.fields['teams'] = forms.ModelMultipleChoiceField(queryset=Clans.objects.filter(id__in=follower_ids), widget=forms.SelectMultiple(attrs={'class': 'select2'}))
        else:
            # Fallback: No followers, empty queryset for 'players'
            self.fields['teams'] = forms.ModelMultipleChoiceField(queryset=Clans.objects.none(), widget=forms.SelectMultiple(attrs={'class': 'select2'}))
    #teams = forms.ModelMultipleChoiceField(queryset=Clans.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select2'}))

   


    
