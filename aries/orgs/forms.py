from django import forms
from .models import Organization

class OrgRegistrationForm(forms.ModelForm):
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
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class OrgsLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
