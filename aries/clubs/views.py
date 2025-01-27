from django.shortcuts import render, redirect, get_object_or_404
from .models import Clans, ClanStats
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from .forms import ClanRegistrationForm, ClanLoginForm
# ============================================================================ #
#                                   important                                  #
# ============================================================================ #
# the clans are clubs to create a pro feel i am calling them club in the htmls but clans in the back
@login_required
def clubs(request):
    """
    Displays a list of clans, sorted by their Elo rating. Supports searching by clan name, ranking, country, or primary game.
    """
    query = request.GET.get('q', '')  # Get the search query from the request
    clans = Clans.objects.all().select_related('stat').order_by('-stat__elo_rating')  # Fetch all clans with their stats, sorted by Elo rating

    if query:
        clans = clans.filter(
            Q(clan_name__icontains=query) |  
            Q(stat__ranking__icontains=query) | 
            Q(country__icontains=query) | 
            Q(primary_game__icontains=query)
        ).distinct()  
    no_results = not clans.exists()  # Check if no clans match the search query
    return render(request, 'clubs/clubs.html', {'query': query, 'clans': clans, 'no_results': no_results})


def club_view(request, clan_id):
    """
    Displays detailed information using the clan_id about a specific clan, including its stats, members, and recent match results.
    """
    clan = get_object_or_404(Clans, id=clan_id)  # Fetch the clan or return a 404 error if not found
    clan_stats = get_object_or_404(ClanStats, id=clan_id)  # Fetch the clan's stats
    match_data = clan_stats.load_match_data_from_file()  # Load match data from the JSON file
    # Process match results for display
    match_results = []
    if match_data:
        for match in match_data["matches"][-5:]:  # Get the last 5 matches
            result = match["result"]
            if result == "win":
                match_results.append("W")  
            elif result == "loss":
                match_results.append("L") 
            else:
                match_results.append("D") 

    members = User.objects.all()  
    context = {
        'clan': clan,
        'stats': clan_stats,
        'players': members,
        "match_results": match_results,
        "match_data": match_data
    }
    return render(request, 'clubs/club_veiw.html', context)


@login_required#ensures only users with accounts can create clubs
def clan_register(request):
    """
    Handles clan registration. Validates the form and creates a new clan if the form is valid.
    """
    if request.method == 'POST':
        form = ClanRegistrationForm(request.POST,request.FILES)  
        if form.is_valid():
            clan = form.save(commit=False)  # Create a clan instance but don't save it yet
            clan.set_password(form.cleaned_data['password'])  # Hash the password
            clan.save()  # Save the clan to the database
            return redirect('clan_login')  # Redirect to the login page after registration
    else:
        form = ClanRegistrationForm()  
    return render(request, 'clubs/create_club.html', {'form': form})


@login_required #ensures only users with accounts can create clubs
def clan_login(request):
    """
    Handles clan login. Validates the form and logs in the clan if the credentials are correct.
    """
    if request.method == 'POST':
        form = ClanLoginForm(request.POST)  
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                clan = Clans.objects.get(email=email)  # Fetch the clan by email
                if clan.check_password(password):  # Verify the password
                    request.session['clan_id'] = clan.id  # Store the clan ID in the session
                    return redirect('clan_dashboard')  # Redirect to the dashboard
                else:
                    form.add_error('password', 'Incorrect password.')  # Add an error for incorrect password
            except Clans.DoesNotExist:
                form.add_error('email', 'Clan not found.')  # Add an error if the clan doesn't exist
    else:
        form = ClanLoginForm()  # Display an empty form for GET requests

    return render(request, 'clubs/clan_login.html', {'form': form})


def clan_logout(request):
    """
    Handles clan logout by clearing the session data and redirecting to the login page.
    """
    request.session.flush()  # Clear all session data
    return redirect('clubs/clan_login')  # Redirect to the login page


def clan_login_required(view_func):
    """
    Custom decorator to ensure that only logged-in clans can access certain views.
    """
    def wrapper(request, *args, **kwargs):
        if 'clan_id' not in request.session:  # Check if the clan is logged in
            return redirect('clubs/clan_login')  # Redirect to the login page if not logged in
        return view_func(request, *args, **kwargs)
    return wrapper


@clan_login_required
def clan_dashboard(request):
    """
    Displays the clan dashboard, including clan details, stats, and match data.
    """
    clan = Clans.objects.get(id=request.session['clan_id'])  # Fetch the logged-in clan
    clan_stats = get_object_or_404(ClanStats, id=request.session['clan_id'])  # Fetch the clan's stats
    match_data = clan_stats.load_match_data_from_file()  # Load match data from the JSON file

    members = User.objects.all() 

    context = {
        'clan': clan,
        'stats': clan_stats,
        'players': members,
        "match_data": match_data
    }
    return render(request, 'clubs/clan_dashboard.html', context)