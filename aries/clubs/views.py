from django.shortcuts import render,redirect
from .models import Clans
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from .forms import ClanRegistrationForm,ClanLoginForm
@login_required
def clubs(request):
    
    context = {
        'clans': Clans.objects.all().order_by('-date_joined')
    }
    
    return render(request, 'clubs/clubs.html', context)
""" def clan_detail(request, clan_id):
    clan = Clans.objects.get(id=clan_id)
    members = clan.members.all()  # All profiles linked to the clan
    return render(request, 'clan_detail.html', {'clan': clan, 'members': members}) """


@login_required
def clan_register(request):
    if request.method == 'POST':
        form = ClanRegistrationForm(request.POST)
        if form.is_valid():
            clan = form.save(commit=False)
            clan.set_password(form.cleaned_data['password'])
            clan.save()
            return redirect('clan_login')  # Redirect to login page after registration
    else:
        form = ClanRegistrationForm()
    return render(request, 'clubs/create_club.html', {'form': form})

@login_required
def clan_login(request):
    if request.method == 'POST':
        form = ClanLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                clan = Clans.objects.get(email=email)
                if clan.check_password(password):
                    request.session['clan_id'] = clan.id  # Store clan ID in session
                    return redirect('clan_dashboard')  # Redirect to dashboard
                else:
                    form.add_error('password', 'Incorrect password.')
            except Clans.DoesNotExist:
                form.add_error('email', 'Clan not found.')
    else:
        form = ClanLoginForm()
    return render(request, 'clubs/clan_login.html', {'form': form})


def clan_logout(request):
    request.session.flush()  # Clear session data
    return redirect('clubs/clan_login') 

def clan_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'clan_id' not in request.session:
            return redirect('clubs/clan_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@clan_login_required
def clan_dashboard(request):
    clan = Clans.objects.get(id=request.session['clan_id'])
    return render(request, 'clubs/clan_dashboard.html', {'clan': clan})