from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile,SocialLink


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False, help_text="Phone number (optional)")

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and Profile.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number is already in use.")
        return phone
    def save(self, commit=True):
        user = super().save(commit)
        phone = self.cleaned_data.get('phone')
        if phone:
            Profile.objects.update_or_create(user=user, defaults={'phone': phone, 'is_verified': False})
        else:
            Profile.objects.create(user=user, defaults={'is_verified': False})

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