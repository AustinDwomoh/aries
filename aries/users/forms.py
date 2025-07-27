from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile,SocialLink
import json

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False, help_text="Phone number (optional, must be unique)")

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit)
        phone = self.cleaned_data.get('phone')
        if phone:
            Profile.objects.update_or_create(user=user, defaults={'phone': phone,'is_verified': False})
        else:
            Profile.objects.get_or_create(user=user, defaults={'is_verified': False})
        return user


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

class CustomLoginForm(forms.Form):
    identifier = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Email / Username / Phone',
        'class': 'form-control',
        'autocomplete': 'username',
    }),
    label='Username')
    password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # pop request, if passed
        super().__init__(*args, **kwargs)