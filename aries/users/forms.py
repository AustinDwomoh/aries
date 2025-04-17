from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
import json

class UserRegisterForm(UserCreationForm):
    """Forms for user account creation"""
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email','password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class SocialLinkForm(forms.Form):
    platform_choices = [
        ('twitter', 'Twitter'),
        ('discord', 'Discord'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('twitch', 'Twitch'),
        # Add more platforms as you like
    ]
    
    platform = forms.ChoiceField(choices=platform_choices, required=True)
    url = forms.URLField(required=True)

    class Meta:
        model = Profile
        fields = ['social_links']
SocialLinkFormSet = modelformset_factory(Profile, form=SocialLinkForm, extra=1)
class ProfileUpdateForm(forms.ModelForm):
    social_links = forms.JSONField(widget=forms.HiddenInput(), required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['profile_picture','social_links']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.social_links:
            # Pre-populate the social links in the form if they exist
            self.fields['social_links'].initial = self.instance.social_links

   