from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile,SocialLink
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

class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ['link_type', 'url']

SocialLinkFormSet = inlineformset_factory(Profile, SocialLink, form=SocialLinkForm, extra=1, can_delete=True)


class ProfileUpdateForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['profile_picture']
