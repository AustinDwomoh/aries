from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm,UserUpdateForm,ProfileUpdateForm
from django.contrib.auth.models import User


# Create your views here.
def register(request):
    """Registration view to create a new user account"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request,f"Your account has been created! You can login")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})



@login_required
def profile(request):
    """Profile view for the logged-in user"""
    try:
        player = User.objects.filter(username__iexact=request.user).first()
        match_data = player.profile.stats.load_match_data_from_file()
        match_results = []
        if match_data:
            for match in match_data["matches"][-5:]:
                result = match["result"]
                if result == "win":
                    match_results.append("W")
                elif result == "loss":
                    match_results.append("L")
                else:
                    match_results.append("D")
    except User.DoesNotExist:
        match = None
    context ={
        "match_data":match_data,
        "match_results":match_results
    }
    return render(request, 'users/profile.html',context)

def logout_view(request):
    """ Logout the user and redirect to home page"""
    logout(request)
    return redirect('Home')

@login_required
def all_gamers(request):
    """View to display all gamers with sorting and search functionality"""
    query = request.GET.get('q', '')
    players = User.objects.select_related('profile__stats').order_by('-profile__stats__elo_rating')
    player_match_results = []
    for player in players:
        player_stats = player.profile.stats  
        match_data = player_stats.load_match_data_from_file()
        
        # Extract match results (W, L, D)
        match_results = []
        if match_data:
            for match in match_data["matches"][-5:]:
                result = match["result"]
                if result == "win":
                    match_results.append("W")
                elif result == "loss":
                    match_results.append("L")
                else:
                    match_results.append("D")
        player_match_results.append({
            "player": player,
            "match_results": match_results
        })

    if query:
        players = players.filter(
            Q(username__icontains=query) | 
            Q(profile__clan__clan_name__icontains=query) |
            Q(profile__stats__rank__icontains=query)
        )
    no_results = not players.exists()
    return render(request,'users/gamers.html',{'players': player_match_results,'query': query,'no_results': no_results})

@login_required
def gamer_view(request,player_id):
    """View to display details of a specific gamer based on player id"""
    player = get_object_or_404(User, id=player_id)
    player_stats = player.profile.stats  
    match_data = player_stats.load_match_data_from_file()
    
    # Extract match results (W, L, D)
    match_results = []
    if match_data:
        for match in match_data["matches"][-5:]:
            result = match["result"]
            if result == "win":
                match_results.append("W")
            elif result == "loss":
                match_results.append("L")
            else:
                match_results.append("D")
  
 
    return render(request,'users/profile_veiw.html',{'player':player,"match_results":match_results,"match_data":match_data})

def edit_profile(request):
    """ Edit profile view"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST,instance=request.user)
        p_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save() 
            p_form.save()
            messages.success(request,f"Your account has been updated!")
            return redirect('user-home')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm()
    return render(request, "users/edit_profile.html",{"u_form":u_form,
        "p_form":p_form,})