from django.shortcuts import render, redirect, get_object_or_404
from .models import Organization
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from .forms import OrgRegistrationForm, OrgsLoginForm

@login_required
def organisation(request):
    """
    View for displaying the list of all organizations (clans).
    Requires the user to be logged in.
    """
    context = {
        'clans': Organization.objects.all().order_by('-date_joined')  # Get all organizations ordered by join date
    }
    return render(request, 'orgs/organisations.html', context)

def org_view(request, org_id):
    """
    View for displaying details of a specific organization.
    """
    org = get_object_or_404(Organization, id=org_id)  # Get the organization or return a 404 error
    return render(request, 'orgs/organisation_view.html', {'org': org})

@login_required
def org_register(request):
    """
    View for organization registration.
    Requires the user to be logged in.
    """
    if request.method == 'POST':
        form = OrgRegistrationForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            org = form.save(commit=False)  
            org.set_password(form.cleaned_data['password'])  # Hash and set the password
            org.save()  # Save the organization to the database
            return redirect('org_login')  # Redirect to the login page after registration
    else:
        form = OrgRegistrationForm() 
    return render(request, 'orgs/create_org.html', {'form': form})

def org_login(request):
    """
    View for organization login.
    """
    if request.method == 'POST':
        form = OrgsLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                org = Organization.objects.get(email=email)  
                if org.check_password(password):  
                    request.session['org_id'] = org.id
                    return redirect('org_dashboard')  
                else:
                    form.add_error('password', 'Incorrect password.') 
            except Organization.DoesNotExist:
                form.add_error('email', 'Organization not found.')  
    else:
        form = OrgsLoginForm() 
    return render(request, 'orgs/org_login.html', {'form': form})

def org_logout(request):
    """
    View for organization logout.
    """
    request.session.flush() 
    return redirect('org_login') 

def org_login_required(view_func):
    """
    Custom decorator to ensure the user is logged in as an organization.
    """
    def wrapper(request, *args, **kwargs):
        if 'org_id' not in request.session: 
            return redirect('org_login')  
        return view_func(request, *args, **kwargs)
    return wrapper

@org_login_required
def org_dashboard(request):
    """
    View for the organization dashboard.
    Requires the user to be logged in as an organization.
    """
    org = Organization.objects.get(id=request.session['org_id'])  
    return render(request, 'orgs/org_dashboard.html', {'org': org})