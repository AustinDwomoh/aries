from django import forms
from .models import Organization

class OrgRegistrationForm(forms.ModelForm):
    """
    A form for registering a new organization. 
    Extends Django's ModelForm and includes additional fields for password confirmation.
    """
    
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Organization
        fields = ['name', 
                  'email', 
                  'password',
                  'short_hand',
                  'org_description',
                  'org_logo',
                  'org_profile_pic',
                  'org_website',
                  'primary_game',
                  'other_games',
                  'country'
                  ]





    def clean(self):
        """
        Custom validation method to ensure the password and confirm_password fields match.
        """
        # Call the parent class's clean method to get the cleaned data
        cleaned_data = super().clean()
        
        # Retrieve the password and confirm_password fields from the cleaned data
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            # Raise a validation error if the passwords do not match
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class OrgsLoginForm(forms.Form):
    """
    A form for organization login. 
    This is a regular Django Form (not a ModelForm) and includes fields for email and password.
    """
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
