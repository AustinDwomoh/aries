from django import forms
from .models import Clans

class ClanRegistrationForm(forms.ModelForm):
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
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class ClanLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
