from django import forms
from .models import Clans
from django.contrib.auth.models import User
from users.models import Profile
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import ClanSocialLink
from django.contrib.auth.models import User
class ClanRegistrationForm(forms.ModelForm):
    """
    Form for registering a new clan.
    Extends ModelForm to create/update Clans model instances.
    Includes password confirmation fields for validation.
    """
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
        """Validate email is unique among User and Clans models."""
        email = self.cleaned_data.get('email')
        # Checks if email already exists in User or Clans tables
        if User.objects.filter(email=email).exists() or Clans.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_phone(self):
        """Validate phone is unique among Profile and Clans models."""
        phone = self.cleaned_data.get('phone')
        # Caution: If phone is None or empty, skip check
        if phone and (Profile.objects.filter(phone=phone).exists() or Clans.objects.filter(phone=phone).exists()):
            raise ValidationError("This phone number is already in use.")
        return phone
    
    def clean(self):
        """
        Override clean() to validate password confirmation.
        Raises a ValidationError if password and confirm_password do not match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class AddPlayerToClanForm(forms.Form):
    """
    Simple form for adding a player to a clan.
    Expects a 'clan' argument on init to filter selectable users to clan members only.
    Uses a select2-enhanced dropdown for better UX.
    """
    def __init__(self, *args, **kwargs):
        clan = kwargs.pop('clan', None)
        super().__init__(*args, **kwargs)

        self.fields['username'] = forms.ModelChoiceField(
                queryset=User.objects.filter(profile__clan=clan),  # Only users already in this clan
                widget=forms.Select(attrs={'class': 'select2', 'style': 'width: 100%;'}),
                empty_label="Select a user"
            )


class ClanSocialLinkForm(forms.ModelForm):
    class Meta:
        model = ClanSocialLink
        fields = ['link_type', 'url', 'display_order', 'is_active']
        widgets = {
            'link_type': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={'placeholder': 'https://example.com', 'class': 'form-control'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


ClanSocialLinkFormSet = inlineformset_factory(
    Clans,             # parent model
    ClanSocialLink,    # child model (has FK to Clans)
    form=ClanSocialLinkForm,
    extra=1,
    can_delete=True
)
class ClanBasicInfoForm(forms.ModelForm):
    class Meta:
        model = Clans
        fields = [
            'clan_name',
            'clan_tag',
            'clan_description',
            'primary_game',
            'other_games',
            'country',
        ]
        widgets = {
            'clan_name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'clan_tag': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'clan_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'primary_game': forms.TextInput(attrs={'class': 'form-control'}),
            'other_games': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ClanContactForm(forms.ModelForm):
    class Meta:
        model = Clans
        fields = [
            'email',
            'clan_website',
            'phone',
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg'}),
            'clan_website': forms.URLInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ClanMediaForm(forms.ModelForm):
    class Meta:
        model = Clans
        fields = ['clan_logo', 'clan_profile_pic']
        widgets = {
            'clan_logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'clan_profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ClanRecruitmentForm(forms.ModelForm):
    class Meta:
        model = Clans
        fields = ['is_recruiting', 'recruitment_requirements']
        widgets = {
            'is_recruiting': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recruitment_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

        # ============================================================================ #
        #                                 Future Ideas                                 #
        # ============================================================================ #
        # You plan to implement an invite system later when you build the PWA.
        # This would let clan leaders invite players who can accept or reject.
        # Only upon acceptance would the player be added to the clan.
        # This approach is better UX and security than just adding players directly.