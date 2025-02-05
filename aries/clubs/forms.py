from django import forms
from .models import Clans
from django.contrib.auth.models import User

class ClanRegistrationForm(forms.ModelForm):
    """Form for clan registration"""
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Clans
        fields = ['clan_name', 
                  'email', 
                  'password',
                  'clan_tag',
                  'clan_description',
                  'clan_logo',
                  'clan_profile_pic',
                  'clan_website',
                  'primary_game',
                  'other_games',
                  'country'
                  ]

    def clean(self):
        """Cleans and hashes the password and checks for confirmatio"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class ClanLoginForm(forms.Form):
    """Form for clan login"""
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class AddPlayerToClanForm(forms.Form):
    """
    Form for selecting a player to add to a clan.
    """
    username = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__clan__isnull=True),  # Users not in any clan
        widget=forms.Select(attrs={'class': 'select2', 'style': 'width: 100%;'}),
        empty_label="Select a user"
    )