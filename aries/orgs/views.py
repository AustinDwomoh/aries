from django.shortcuts import render,redirect,get_object_or_404
from .models import Organization
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from .forms import OrgRegistrationForm,OrgsLoginForm
@login_required
def organisation(request):
    
    context = {
        'clans': Organization.objects.all().order_by('-date_joined')
    }
    
    return render(request, 'orgs/organisations.html', context)
""" def clan_detail(request, clan_id):
    clan = Clans.objects.get(id=clan_id)
    members = clan.members.all()  # All profiles linked to the clan
    return render(request, 'clan_detail.html', {'clan': clan, 'members': members}) """


def org_view(request,org_id):
    """ clan_members = get_object_or_404(Clans, id=clan_id)
    clan = get_object_or_404(Clans, id=clan_id)
    clan_stats = get_object_or_404(ClanStats, id=clan_id)
    members = User.objects.all()
    context = {
        'clan' : clan,
        'stats': clan_stats,
        'players':members
    } """
    return render(request, 'orgs/organistaion_veiw.html')

@login_required
def org_register(request):
    if request.method == 'POST':
        form = OrgRegistrationForm(request.POST)
        if form.is_valid():
            org = form.save(commit=False)
            org.set_password(form.cleaned_data['password'])
            org.save()
            return redirect('org_login')  # Redirect to login page after registration
    else:
        form = OrgRegistrationForm()
    return render(request, 'orgs/create_org.html', {'form': form})

@login_required
def org_login(request):
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
                form.add_error('email', 'Org not found.')
    else:
        form = OrgsLoginForm()
    return render(request, 'orgs/org_login.html', {'form': form})


def org_logout(request):
    request.session.flush()  # Clear session data
    return redirect('orgs/org_login') 

def org_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'org_id' not in request.session:
            return redirect('orgs/org_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@org_login_required
def org_dashboard(request):
    org = Organization.objects.get(id=request.session['org_id'])
    return render(request, 'orgs/org_dashboard.html', {'org': org})