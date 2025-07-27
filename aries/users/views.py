from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from itertools import chain
from django.db.models import Q
from django.contrib.auth import logout,login,authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm,UserUpdateForm,ProfileUpdateForm, SocialLinkFormSet,CustomLoginForm
from tournaments.models import ClanTournament, IndiTournament,ClanTournamentPlayer
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.contrib.contenttypes.models import ContentType
from Home.models import Follow
from clans.models import Clans
from django.contrib.auth.views import LoginView
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from users import verify


# Create your views here.
def register(request):
    """Registration view to create a new user account"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.save()
            verify.send_verification(user)
                
            messages.success(request,f"Your account has been created! You can login")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

@login_required
def profile(request):
    """Profile view for the logged-in user"""

    player = User.objects.filter(username__iexact=request.user).first()
    match_data = player.profile.stats.load_match_data_from_file()
    match_results = []
    followed_type = ContentType.objects.get_for_model(Clans)

    followers = Follow.objects.filter(followed_type=followed_type, followed_id=player.profile.id).count()
    following = Follow.objects.filter(follower_type=followed_type, follower_id=player.id).count()
    player_tour_ids = ClanTournamentPlayer.objects.filter(user=request.user).values_list('tournament_id', flat=True)
    cvc_tournaments =  ClanTournament.objects.filter(Q(created_by=request.user) | Q(id__in=player_tour_ids)).distinct().order_by('-id')[:5]
    indi_1 = IndiTournament.objects.filter(created_by=request.user).order_by('-id')[:5]
    indi_2 = IndiTournament.objects.filter(players=request.user.profile).order_by('-id')[:5]
    combined = list(chain(indi_1, indi_2))
    indi_tournaments = sorted(set(combined), key=lambda x: x.id, reverse=True)[:5]

    if match_data:
        for match in match_data["matches"][-5:]:
            result = match["result"]
            if result == "win":
                match_results.append("W")
            elif result == "loss":
                match_results.append("L")
            else:
                match_results.append("D")
        match_data["matches"] = match_data["matches"][:5]
    query = request.GET.get('q', '')
    if query:
        # Filter players using list comprehension
        match_data["matches"] = [
        match for match in match_data['matches']
        if (query.lower() in match['date'].lower() or
            query.lower() in match['tour_name'].lower() or
            query.lower() in match['opponent'].lower() or
            query.lower() in match['result'].lower() or
            query.lower() in match['score'].lower())
        ]
   #bad i know but this is the best way i could think of slicing it

    
    context ={
        "match_data":match_data,
        "match_results":match_results,
        'query':query,
        'followers':followers,
        'following':following,
        'indi_tournaments':indi_tournaments,
        'cvc_tournaments':cvc_tournaments
        
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
    followed_type = ContentType.objects.get_for_model(User)

    followers = Follow.objects.filter(followed_type=followed_type, followed_id=player_id).count()
    following = Follow.objects.filter(follower_type=followed_type, follower_id=player_id).count()
    is_following =  Follow.objects.filter(followed_type=followed_type, followed_id=player_id, follower_id=request.user.id).exists()
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
        match_data["matches"] = match_data["matches"][:5]
    query = request.GET.get('q', '')
    if query:
        # Filter players using list comprehension
        match_data["matches"] = [
        match for match in match_data['matches']
        if (query.lower() in match['date'].lower() or
            query.lower() in match['tour_name'].lower() or
            query.lower() in match['opponent'].lower() or
            query.lower() in match['result'].lower() or
            query.lower() in match['score'].lower())
        ]
   #bad i know but this is the best way i could think of slicing it
    
    context ={
        'player':player,
        "match_results":match_results,
        "match_data":match_data,
        'query':query,
        'followers':followers,
        'following':following,
        'is_following': is_following
        }
  
 
    return render(request,'users/profile_veiw.html',context)



def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        social_formset = SocialLinkFormSet(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid() and social_formset.is_valid():
            u_form.save()
            p_form.save()
            social_formset.save()

            messages.success(request, "Your account has been updated!")
            return redirect('user-home')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
        social_formset = SocialLinkFormSet(instance=profile)

    return render(request, 'users/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'social_formset': social_formset,
    })

@login_required
def follow_unfollow(request, action, followed_model, followed_id):
    """
    Allows a user or a club to follow or unfollow another user or club dynamically.
    :param action: "follow" or "unfollow"
    :param followed_id: ID of the entity being followed or unfollowed
    """
    # Determine follower type
    if isinstance(request.user, User):
        follower_type = ContentType.objects.get_for_model(User)
        follower_id = request.user.id
        
    else:
        follower_type = ContentType.objects.get_for_model(Clans)
        follower_id = request.clan.id 
   
    # Get the followed entity
    if followed_model == "user":
        
        followed_obj = get_object_or_404(User, id=followed_id)
    else:
        return JsonResponse({"error": "Invalid model type"}, status=400)
    followed_type = ContentType.objects.get_for_model(followed_obj)

    if action == "follow":
        follow, created = Follow.objects.get_or_create(
            follower_type=follower_type,
            follower_id=follower_id,
            followed_type=followed_type,
            followed_id=followed_obj.id
        )
       
        if created:
            
            return JsonResponse({"context": {"message": f"You are now following {followed_model} with ID {followed_id}"}})
        return JsonResponse({"context": {"message": f"Already following {followed_model} with ID {followed_id}"}})
    
    elif action == "unfollow":
        deleted, _ = Follow.objects.filter(
            follower_type=follower_type,
            follower_id=follower_id,
            followed_type=followed_type,
            followed_id=followed_obj.id
        ).delete()
        if deleted:
            return JsonResponse({"context": {"message": f"You have unfollowed {followed_model} with ID {followed_id}"}})
        return JsonResponse({"context": {"message": "You weren't following this entity"}})

    return JsonResponse({"error": "Invalid action"}, status=400)



class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'users/login.html' 

    def form_valid(self, form):
        identifier = form.cleaned_data.get('identifier')
        password = form.cleaned_data.get('password')
        remember = self.request.POST.get('remember_me')

        user = authenticate(self.request, username=identifier, password=password)

        if user is not None:
            login(self.request, user)
            verify.send_verification(user)#custom
            if remember:
                self.request.session.set_expiry(60 * 60 * 24 * 7)  
            else:
                self.request.session.set_expiry(0)  # Until browser is closed

            return redirect(self.get_success_url())
        else:
            form.add_error(None, "Invalid credentials")
            return self.form_invalid(form)

def verify_phone(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        user = request.user  
        stored = cache.get(f"phone_otp_{user.pk}")

        if stored == otp:
            user.profile.is_verified = True  
            user.profile.save()
            cache.delete(f"phone_otp_{user.pk}")
            return redirect('login')  
        else:
            return HttpResponse("Invalid OTP")

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.profile.is_verified = True
        user.profile.save()
        return redirect('login')
    else:
        return HttpResponse("Invalid or expired link.")