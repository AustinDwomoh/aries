from django import forms
from .models import Clans
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import ClanSocialLink
from django.contrib.auth.models import User
from django_countries.widgets import CountrySelectWidget


class ClanBasicsForm(forms.ModelForm):
    class Meta:
        model = Clans
        fields = ['clan_name', 'clan_tag', 'clan_description']
        widgets = {
            'clan_name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'clan_tag': forms.TextInput(attrs={'class': 'form-control'}),
            'clan_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
class ClanContactForm(forms.Form):
    email = forms.EmailField(
    widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter email address'
    }),
    help_text="You can reuse your main Gmail by adding +clan (e.g. yourname+clan@gmail.com).")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    
    def clean_email(self):
        """Validate email is unique among User and Clans models."""
        email = self.cleaned_data.get('email')
        # Checks if email already exists in User or Clans tables
        if User.objects.filter(email=email).exists() or Clans.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
    def clean(self):
        """
        Override clean() to validate password confirmation.
        Raises a ValidationError if password and confirm_password do not match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

class ClanMediaForm(forms.ModelForm):
    class Meta:
        model = Clans
        fields = ['clan_logo', 'clan_profile_pic']
        widgets = {
            'clan_logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'clan_profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ClanExtrasForm(forms.ModelForm):
    class Meta:
        model = Clans
        fields = ['clan_website', 'primary_game', 'other_games', 'country']
        widgets = {
            'clan_website': forms.URLInput(attrs={'class': 'form-control'}),
            'primary_game': forms.TextInput(attrs={'class': 'form-control'}),
            'other_games': forms.TextInput(attrs={'class': 'form-control'}),
            'country': CountrySelectWidget(attrs={'class': 'form-control'}),
        }

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
        fields = ['link_type', 'url']
        widgets = {
            'link_type': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={'placeholder': 'https://example.com', 'class': 'form-control'}),
        }

ClanSocialLinkFormSet = inlineformset_factory(
    Clans,             # parent model
    ClanSocialLink,    # child model (has FK to Clans)
    form=ClanSocialLinkForm,
    extra=1,
    can_delete=True
)
class ClanRecruitmentForm(forms.ModelForm):
    class Meta:
        model = Clans
        fields = ['is_recruiting', 'recruitment_requirements']
        widgets = {
            'is_recruiting': forms.CheckboxInput(attrs={
                'class': 'form-check-input me-2',  # small margin for label
            }),
            'recruitment_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add recruitment requirements here…',
                'style': 'resize: vertical;',
            }),
        }
        labels = {
            'is_recruiting': 'Open for Recruitment?',
            'recruitment_requirements': 'Recruitment Requirements',
        }

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
            'country': CountrySelectWidget(attrs={'class': 'form-control'}),
        }

class ClanContactFormEdit(forms.ModelForm):
    class Meta:
        model = Clans
        fields = [
            'email',
            'clan_website',
            
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg'}),
            'clan_website': forms.URLInput(attrs={'class': 'form-control'}),
        }
