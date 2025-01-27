from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    """Forms for user account creation"""
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email','password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    """Right now just email update from """
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['email']

class ProfileUpdateForm(forms.ModelForm):
    """Right now just profile_pic update from """
    class Meta:
        model = Profile
        fields = ["profile_picture"]