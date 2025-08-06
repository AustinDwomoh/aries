from django import forms
from .models import Clans
from django.contrib.auth.models import User
from users.models import Profile
from django.core.exceptions import ValidationError
class ClanRegistrationForm(forms.ModelForm):
    """Form for clan registration"""
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Clans
        fields = ['clan_name', 
                  'email',
                  'phone',
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
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() or Clans.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and Profile.objects.filter(phone=phone).exists() or Clans.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number is already in use.")
        return phone
    
    def clean(self):
        """Cleans and hashes the password and checks for confirmatio"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class AddPlayerToClanForm(forms.Form):
    """
    Form for selecting a player to add to a clan.
    """
    def __init__(self, *args, **kwargs):
        clan = kwargs.pop('clan', None)
        super().__init__(*args, **kwargs)

        self.fields['username'] = forms.ModelChoiceField(
                queryset=User.objects.filter(profile__clan=clan),  # Filter users that are in the clan
                widget=forms.Select(attrs={'class': 'select2', 'style': 'width: 100%;'}),
                empty_label="Select a user"
            )
        # ============================================================================ #
        #                                 Future Ideas                                 #
        # ============================================================================ #
        #make it an invite system when you implement the PWA
        #so you invite and when they accpet you get it