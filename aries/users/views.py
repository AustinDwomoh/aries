from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from itertools import chain
from django.db.models import Q
from django.contrib.auth import logout,login
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm,UserUpdateForm,ProfileUpdateForm, SocialLinkFormSet,CustomLoginForm
from tournaments.models import ClanTournament, IndiTournament,ClanTournamentPlayer
from django.contrib.auth.models import User
from django.http import  JsonResponse
from django.contrib.auth.views import LoginView
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from scripts import verify,follow
from scripts.context import make_social_links_dict 
from scripts.error_handle import ErrorHandler
from django.db import transaction
from threading import Thread
from clans.models import Clans
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import SocialLink
# Create your views here.
def register(request):
    """Registration view to create a new user account"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    request.session['pending_verification'] = user.email or user.username
                    request.session['pending_model'] = 'user'  # Store model type for verification
                    Thread(target=verify.send_verification,kwargs={"account": user, "model_type": 'user', "method": 'email'}).start()

                    messages.info(request, "We've sent you a verification email.")
                    return redirect('verification_pending')
                
            except Exception as e:
                ErrorHandler().handle(e, 'Registration failure')
                messages.error(request, "Something went wrong. Please try again or contact support.")
                return redirect('register')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

@login_required
def profile(request):
    """Profile view for the logged-in user"""
    match_data = {"matches": []}
    match_results = []
    indi_tournaments = []
    cvc_tournaments = []
    query = request.GET.get('q', '')
    socials = {}
    try:
        player = request.user
        match_data = player.profile.stats.load_match_data_from_file()
        match_results = []
        followers = follow.count_followers(player)
        following = follow.count_following(player)
        player_tour_ids = ClanTournamentPlayer.objects.filter(user=request.user).values_list('tournament_id', flat=True)
        cvc_tournaments =  ClanTournament.objects.filter(Q(created_by=request.user) | Q(id__in=player_tour_ids)).distinct().order_by('-id')[:5]
        indi_1 = IndiTournament.objects.filter(created_by=request.user).order_by('-id')[:5]
        indi_2 = IndiTournament.objects.filter(players=request.user.profile).order_by('-id')[:5]
        combined = list(chain(indi_1, indi_2))
        indi_tournaments = sorted(set(combined), key=lambda x: x.id, reverse=True)[:5]
        socials = make_social_links_dict(SocialLink.objects.filter(profile=player.profile).all())
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
        if query:
            query_lower = query.lower()
            filtered_matches = []
            for match in match_data["matches"]:
                if any(query_lower in (match.get(field, "") or "").lower()
                        for field in ['date', 'tour_name', 'opponent', 'result', 'score']):
                    filtered_matches.append(match)
            match_data["matches"] = filtered_matches
   
    except Exception as e:
        messages.error(request,'There has been an error loading your profile')
        ErrorHandler().handle(e,context=f"Profile loading for {request.user.username}")
    
    context ={
        "match_data":match_data,
        "match_results":match_results,
        'query':query,
        'followers':followers,
        'following':following,
        'indi_tournaments':indi_tournaments,
        'cvc_tournaments':cvc_tournaments,
        'socials':socials,
        
    }
    return render(request, 'users/profile.html',context)

def logout_view(request):
    """ Logout the user and redirect to home page"""
    logout(request)
    return redirect('Home')

@login_required
def all_gamers(request):
    """View to display all gamers with sorting and search functionality"""
    query = request.GET.get('q', '').strip()
    players = []
    no_results = False

    try:
        players_qs = User.objects.select_related('profile__stats').all()
        if request.session.get("is_user"):
            user_id = request.session.get("user_id")
            if user_id:
                players_qs = players_qs.exclude(id=user_id)
        if query:
            players_qs = players_qs.filter(
                Q(username__icontains=query) | 
                Q(profile__clan__clan_name__icontains=query) |
                Q(profile__stats__rank__icontains=query)
            )
        
        players_qs = players_qs.order_by('-profile__stats__elo_rating')

        for player in players_qs:
            player_stats = getattr(player.profile, 'stats', None)
            match_data = None
            match_results = []

            if player_stats:
                match_data = player_stats.load_match_data_from_file()

            if match_data and "matches" in match_data:
                recent_matches = match_data["matches"][-5:]
                for match in recent_matches:
                    result = match.get("result", "").lower()
                    if result == "win":
                        match_results.append("W")
                    elif result == "loss":
                        match_results.append("L")
                    else:
                        match_results.append("D")
            background_image = player.profile.clan.clan_profile_pic.url if player.profile.clan and player.profile.clan.clan_profile_pic else '/static/images/areis-1.png'
            players.append({
                "player": player,
                "background_image": background_image,
                "match_results": match_results,
            })

        no_results = not players_qs.exists()

    except Exception as e:
        messages.error(request, "An error occurred while loading gamers.")
        ErrorHandler().handle(e, context="all_gamers view")

    context = {
        'players': players,
        'query': query,
        'no_results': no_results,
    }
    return render(request,'users/gamers.html',context)

@login_required
def gamer_view(request,player_id):
    """View to display details of a specific gamer based on player id"""
    player = get_object_or_404(User, id=player_id)
    player_stats = player.profile.stats  
    match_data = player_stats.load_match_data_from_file()
    socials = make_social_links_dict(SocialLink.objects.filter(profile=player.profile).all())
    followers = follow.count_followers(player)
    following = follow.count_following(player)
    is_following =  follow.is_follower(follow.get_logged_in_entity(request),player)
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
    context ={
        'player':player,
        "match_results":match_results,
        "match_data":match_data,
        'query':query,
        'followers':followers,
        'following':following,
        'is_following': is_following,
        'followed': player,     
        'model_name': 'user',
        "show_button": request.user != player,
        "follow_type": "user",
        'socials':socials,
        }
  
 
    return render(request,'users/profile_veiw.html',context)

@login_required
def edit_profile(request):
    profile = request.user.profile
    try:
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            pass_form = PasswordChangeForm(request.user, request.POST)
            social_formset = SocialLinkFormSet(request.POST, instance=profile)

            any_changes = False
            with transaction.atomic():
                if u_form.is_valid():
                    u_form.save()
                    any_changes = True
                if p_form.is_valid():
                    p_form.save()
                    any_changes = True
                if social_formset.is_valid():
                    social_formset.save()
                    any_changes = True
                if pass_form.is_valid():
                    user = pass_form.save()
                    update_session_auth_hash(request, user)
                    any_changes = True
    
            if any_changes:
                messages.success(request, "Your changes have been saved.")
                return redirect('edit_profile')
            else:
                messages.error(request, "No changes saved. Please fix the errors.")
                return redirect('user-home')

        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=profile)
            pass_form = PasswordChangeForm(request.user)
            social_formset = SocialLinkFormSet(instance=profile)
    except Exception as e:
        messages.error(request, "There was an error updating your profile.")
        ErrorHandler().handle(e, context=f"edit_profile view for user {request.user.username}")
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
        social_formset = SocialLinkFormSet(instance=profile)
        pass_form = PasswordChangeForm(request.user)

    return render(request, 'users/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'pass_form': pass_form,
        'social_formset': social_formset,
    })

@login_required
def follow_toggle_view(request, action, model, obj_id):
    try:
        current_entity = follow.get_logged_in_entity(request)
        target = follow.get_followed_instance(model, obj_id)

        if action == "follow":
            follow_obj, created = follow.follow(current_entity, target)
            message = f"You followed {target}"
        elif action == "unfollow":
            follow.unfollow(current_entity, target)
            message = f"You unfollowed {target}"
        else:
            return JsonResponse({"context": {"message": "Invalid action"}}, status=400)
        return JsonResponse({"context": {"message": message}})
    except Exception as e:
        ErrorHandler().handle(e, context='User Follow/Unfollow')
        return JsonResponse({"error": "Unexpected error occurred."}, status=500)
 
class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'users/login.html' 
    def form_valid(self, form):
        identifier = form.cleaned_data.get('identifier')
        password = form.cleaned_data.get('password')
        remember = self.request.POST.get('remember_me')

        # Try authenticating user first
        try:
            auth_backend = verify.MultiFieldAuthBackend()
            user, reason = auth_backend.custom_authenticate(request=self.request, username=identifier, password=password)
            if reason == 'unverified':
                user_obj = User.objects.filter(
                    Q(username=identifier) | Q(email=identifier) | Q(profile__phone=identifier)
                ).first()
                messages.info(self.request, 'Account not verified. Check your email.')
                Thread(target=verify.send_verification, kwargs={"account": user_obj, "model_type": 'user', "method": 'email'}).start()
                self.request.session['pending_verification'] = identifier
                self.request.session['pending_model'] = 'user'  # Store model type for verification
                return redirect('verification_pending')

            if user:
                login(self.request, user)
                self.request.session['is_user'] = True
                self.request.session['user_id'] = user.id
                self.request.session.set_expiry(60 * 60 * 24 * 7 if remember else 0)
                return redirect("user-home")

        except Exception as e:
            ErrorHandler().handle(e, context="Error during user login attempt")

        # Try authenticating as clan
        try:
            clan_backend = verify.ClanBackend()
            clan,reason = clan_backend.custom_authenticate(self.request, username=identifier, password=password)
            if reason == 'unverified':
                clan_obj = Clans.objects.filter(
                    Q(clan_name=identifier) | Q(email=identifier) | Q(phone=identifier)
                ).first()
                messages.info(self.request, 'Account not verified. Check your email.')
                Thread(target=verify.send_verification, kwargs={"account": clan_obj, "model_type": 'clan', "method": 'email'}).start()
                self.request.session['pending_verification'] = identifier
                self.request.session['pending_model'] = 'clan'  # Store model type for verification
                return redirect('verification_pending')
            if clan:
                login(self.request, clan)
                self.request.session['is_clan'] = True
                self.request.session['clan_id'] = clan.id
                self.request.session.set_expiry(60 * 60 * 24 * 7 if remember else 0)
                return redirect('clan_dashboard')
        except Exception as e:
            ErrorHandler().handle(e, context="Error during clan login attempt")

        # If neither worked
        form.add_error(None, "Invalid credentials")
        return self.form_invalid(form)

def verify_otp(request):
    if request.method == "POST":
        try:
            otp = request.POST.get("otp", "").strip()
            identifier = request.session.get("pending_verification")
            model_type = request.session.get("pending_model") 
            if not identifier or not model_type:
                messages.error(request, "Verification session expired. Please try again.")
                return redirect("verification_pending")

            account = None
            if model_type == "user":
                account = User.objects.filter(
                    Q(username__iexact=identifier) |
                    Q(email__iexact=identifier) |
                    Q(profile__phone__iexact=identifier)
                ).first()
            elif model_type == "clan":
                account = Clans.objects.filter(
                    Q(clan_name__iexact=identifier) |
                    Q(email__iexact=identifier)
                ).first()

            if not account:
                messages.error(request, f"{model_type.title()} not found for verification.")
                return redirect("verification_pending")

            stored = cache.get(f"{model_type}_otp_{account.pk}")
          
            if stored and otp == stored:
                if model_type == "user":
                    account.profile.is_verified = True
                    account.profile.save()
                else:  # clan
                    account.is_verified = True
                    account.save()

                cache.delete(f"{model_type}_otp_{account.pk}")
                messages.success(request, f"Your {model_type} account has been verified.")
                return redirect("login")
            else:
                messages.error(request, "Invalid OTP.")
                return redirect("verification_pending")

        except Exception as e:
            ErrorHandler().handle(e, context=f"OTP verification for {identifier} ({model_type})")
            messages.error(request, "Something went wrong during verification. Try again.")
            return redirect("verification_pending")

    return redirect("login")
def verify_email(request, model_type, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        account = None

        if model_type == "user":
            account = User.objects.filter(pk=uid).first()
        elif model_type == "clan":
            account = Clans.objects.filter(pk=uid).first()
        if not account:
            messages.error(request, "Invalid verification link.")
            return render(request, "users/verification_failed.html")

        if default_token_generator.check_token(account, token):
            if model_type == "user":
                account.profile.is_verified = True
                account.profile.save()
            else:
                account.is_verified = True
                account.save()
            return render(request, "users/verification_success.html")
        else:
            return render(request, "users/verification_failed.html")

    except Exception as e:
        ErrorHandler().handle(e, context=f"Email verification attempt failed for {model_type}:{uidb64}")
        return render(request, "users/verification_failed.html")

def verification_pending(request):
    identifier = request.session.get('pending_verification')
    if not identifier:
        return redirect('login')  # fallback

    user = User.objects.filter(
        Q(username__iexact=identifier) | 
        Q(email__iexact=identifier) |
        Q(profile__phone__iexact=identifier)
    ).first()

    clan = Clans.objects.filter(
        Q(clan_name__iexact=identifier) |
        Q(email__iexact=identifier) 
    ).first()
    account = user or clan
    is_verified = (account.profile.is_verified if user else getattr(account, 'is_verified', False) )
      # Use whichever exists

    if not account:
        messages.error(request, "No account found for verification.")
        return redirect('login')
    if is_verified:
        messages.info(request, "Your account is already verified.")
        return redirect('login')

    return render(request, 'users/verification_pending.html', {'user': user,'clan':clan})

def resend_verification(request):
    if request.method == 'POST':
        method = request.POST.get('method')
        identifier = request.session.get('pending_verification')

        if not identifier or not method:
            messages.error(request, "Invalid request.")
            return redirect('login')

        user = User.objects.filter(
            Q(username__iexact=identifier) |
            Q(email__iexact=identifier) |
            Q(profile__phone__iexact=identifier)
        ).first()

        clan = Clans.objects.filter(
        Q(clan_name__iexact=identifier) |
        Q(email__iexact=identifier) 
        ).first()
        account = clan or user
        model = 'user' if user else 'clan'
        if not account:
            messages.error(request, "No account found for verification.")
            return redirect('login')

        if model == "user":
            is_verified = account.profile.is_verified
        else:  # clan
            is_verified = getattr(account, "is_verified", False)
        if is_verified:
            messages.info(request, "Your account is already verified.")
            return redirect('login')

        try:
            Thread(target=verify.send_verification, kwargs={"account": account,'model_type':model,'method':'email'}).start()
            messages.success(request, f"Verification sent via {method}.")
        except Exception as e:
            ErrorHandler().handle(e, context=f"Resend verification failed for {getattr(account, 'username', getattr(account, 'clan_name', 'Unknown'))}")
            messages.error(request, "Failed to resend verification. Try again later.")
        return redirect('verification_pending')
    return redirect('login')
