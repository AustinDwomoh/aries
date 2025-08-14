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
        if commit:
            user.refresh_from_db()  
            if phone:
                user.profile.phone = phone
            user.profile.is_verified = False
            user.profile.save()

        return user

class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ['link_type', 'url', 'display_order', 'is_active']
        widgets = {
            'link_type': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={'placeholder': 'https://example.com', 'class': 'form-control'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


SocialLinkFormSet = inlineformset_factory(
    Profile,            
    SocialLink,         
    form=SocialLinkForm,
    extra=1,            
    can_delete=True     
)

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ['username','email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg'}),
        }
        
class ProfileUpdateForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False)
    phone = forms.CharField(required=False)
    class Meta:
        model = Profile
        fields = ['profile_picture','phone']
        widgets = {
            'profile_picture': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'phone': forms.EmailInput(attrs={'class': 'form-control form-control-lg'}),
        }

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