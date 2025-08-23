from django.shortcuts import render, redirect, get_object_or_404
from .models import Clans, ClanStats,ClanJoinRequest,ClanSocialLink
from django.utils.safestring import mark_safe
import markdown,os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from tournaments.models import ClanTournament
from django.contrib.auth.models import User
from users.models import Profile
from scripts.follow import *
from django.views.decorators.http import require_POST
from scripts import verify
from scripts.context import make_social_links_dict
from django.contrib.auth.decorators import login_required
from .forms import *
from django.http import JsonResponse
from django.db.models import Q
from scripts.error_handle import ErrorHandler
from django.contrib import messages
from django.db import transaction
from threading import Thread
from formtools.wizard.views import SessionWizardView
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth import update_session_auth_hash
def clan_login_required(view_func):
    """
    Custom decorator to ensure that only logged-in clans can access certain views.
    """
    def wrapper(request, *args, **kwargs):
        if 'clan_id' not in request.session:  
            return redirect('login')  
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def clans(request):
    """
        Displays a list of verified clans, optionally filtered by a search query.
        The clans are sorted by their Elo rating (presumably handled elsewhere, maybe in template or queryset).
        Users who are logged in as a clan (session 'is_clan') will have their own clan excluded from the list
        to avoid showing themselves.

        Supports searching clans by:
        - clan_name (case-insensitive partial match)
        - ranking (accessed via related 'stat' model)
        - country (case-insensitive partial match)
        - primary_game (case-insensitive partial match)

        If no clans match the search, a 'no_results' flag is set for the template.

        Error handling is done by catching any exceptions and passing them to a custom ErrorHandler.

        Args:
            request: Django HttpRequest object

        Returns:
            HttpResponse with rendered 'clans/clans.html' template and context including:
            - query: the search term (empty string if none)
            - clans: queryset of matching Clan objects
            - no_results: boolean indicating if the query returned no clans
    """
    query = request.GET.get('q', '')
    clans = Clans.objects.none()  
    no_results = True

    try:
        clans = Clans.objects.filter(is_verified=True)
        #to avoid users cuasing any potential follow issues
        if request.session.get('is_clan'):
            clan_id = request.session.get('clan_id')
            if clan_id:
                clans = clans.exclude(id=clan_id)
        if query:
            clans = clans.filter(
                Q(clan_name__icontains=query) |
                Q(stat__rank__icontains=query) |
                Q(country__icontains=query) |
                Q(primary_game__icontains=query)
            ).distinct()
        
        no_results = not clans.exists()

    except Exception as e:
        ErrorHandler().handle(e, context='Clans loading view')

    return render(request, 'clans/clans.html', {
        'query': query,
        'clans': clans,
        'no_results': no_results
    })

@login_required
def request_to_join_clan(request, clan_id):
    """
    Allows a logged-in player (user) to request joining a specific clan.
    
    Process:
    - Checks if the clan exists (404 if not).
    - Prevents duplicate pending requests from the same player to the same clan.
    - Creates a new join request with status 'pending'.
    - Returns JSON responses with success or error messages.
    - Uses error handling to catch unexpected issues and log them.
    
    Args:
        request: Django HttpRequest object (must be authenticated user).
        clan_id: Integer ID of the clan to join.
    
    Returns:
        JsonResponse with:
        - 200 status and confirmation message if request is successfully created.
        - 400 status and message if a pending request already exists.
        - 500 status and generic error message if something unexpected happens.
    """
    try:
        clan = get_object_or_404(Clans, id=clan_id)
       
        if ClanJoinRequest.objects.filter(player=request.user, clan=clan, status="pending").exists():
            return JsonResponse({"message": "You have already requested to join this clan. Contact admin if possible"}, status=400)

        ClanJoinRequest.objects.create(player=request.user, clan=clan)
        subject = "Join Request"
        body = f"{request.user.username} has requested to join your clan."

        html_content = render_to_string("clans/member_notify.html", {
            "member_name": request.user.username,
            "clan_name": clan.clan_name,
            "profile_link":request.build_absolute_uri(f"/users/gamer_view/{request.user.pk}/"),
            "action":"request"
        })

        # Send asynchronously
        threading.Thread(
            target=email_handle.send_email_with_attachment,
            kwargs={
                "subject": subject,
                "body": body,
                "to_email": clan.email,
                "file_path": None,
                "from_email": None,
                "html_content": html_content
            }
        ).start()
        return JsonResponse({"message": "Request sent"}, status=200)

    except Exception as e:
        ErrorHandler().handle(e, context='Joining clan request')
        return JsonResponse({"message": "An error occurred while processing your request."}, status=500)

@login_required
def leave_clan(request,clan_id):
    """
    Allows a logged-in player to leave their current clan.

    Process:
    - Fetches the user's profile.
    - Removes the clan association by setting profile.clan to None.
    - Saves the updated profile.
    - Adds a success message on successful operation.
    - On failure, logs the error and adds an error message.
    - Redirects the user back to the clan home page.

    Args:
        request: Django HttpRequest (user must be logged in).
        clan_id: ID of the clan to leave 

    Returns:
        HttpResponseRedirect to 'clan_home'.
    """
    try:
        profile = User.objects.get(username=request.user.username).profile
        clan = profile.clan
        if not profile.clan or profile.clan.id != clan_id:
            messages.error(request, "You are not a member of this clan.")
            return redirect("clan_home")
        profile.clan = None
        profile.save()
        subject = "A Member Has Left Your Clan"
        body = f"{profile.user.username} has left your clan."

        html_content = render_to_string("clans/member_notify.html", {
            "member_name": profile.user.username,
            "clan_name": clan.clan_name,
            "profile_link": request.build_absolute_uri(f"/users/gamer_view/{profile.pk}/"),
            "action":"left"
        })

        # Send asynchronously
        threading.Thread(
            target=email_handle.send_email_with_attachment,
            kwargs={
                "subject": subject,
                "body": body,
                "to_email": clan.email,
                "file_path": None,
                "from_email": None,
                "html_content": html_content
            }
        ).start()
        messages.success(request, 'You have successfully left the clan.')
    except Exception as e:
        ErrorHandler().handle(e, context='Leaving Clan')
        messages.error(request, 'An error occurred while trying to leave the clan.')
    return redirect("clan_home")


@login_required
def clan_view(request, clan_id):
    """
    Display detailed information about a clan including stats, members, tournaments, and recent matches.

    Args:
        request: HttpRequest object.
        clan_id: ID of the clan to display.

    Returns:
        Rendered clan detail page or error page.
    """
    try:
        clan = get_object_or_404(Clans, id=clan_id)
        clan_stats = get_object_or_404(ClanStats, id=clan_id)
        match_data = clan_stats.load_match_data_from_file()
        clan.clan_description = mark_safe(markdown.markdown(clan.clan_description))
        followers = count_followers(clan)
        following = count_following(clan)
        is_following = is_follower(get_logged_in_entity(request),clan)
        
        socials  = make_social_links_dict(ClanSocialLink.objects.filter(clan=clan).all())
        tournaments = ClanTournament.objects.filter(teams=clan).order_by('-id')[:5]
        
        match_results = []
        if match_data and "matches" in match_data:
            last_5_matches = match_data["matches"][-5:]
            match_results = [
                "W" if m["result"] == "win" else "L" if m["result"] == "loss" else "D"
                for m in last_5_matches
            ]
            match_data["matches"] = last_5_matches

        query = request.GET.get('q', '')
        if query:
            q_lower = query.lower()
            match_data["matches"] = [
                m for m in match_data["matches"]
                if any(q_lower in str(m[f]).lower() for f in ['date', 'tour_name', 'opponent', 'result', 'score'])
            ]

        members = User.objects.filter(profile__clan=clan)
        context = {
            'clan': clan,
            'stats': clan_stats,
            'players': members,
            'tournaments': tournaments,
            "match_results": match_results,
            "match_data": match_data,
            'query': query,
            'followers': followers,
            'following': following,
            'is_following': is_following,
            'socials': socials,
        }

        return render(request, 'clans/clan_view.html', context)

    except Exception as e:
        ErrorHandler().handle(e, context='clan_view')
        return render(request, 'clans/clan_view.html', {
            'error': "Something went wrong while loading the clan view."
        })

@clan_login_required
def clan_dashboard(request):
    """
    Renders the dashboard for the logged-in clan.

    Retrieves clan details, statistics, members, tournaments, join requests,
    recent match data, and follower counts. Supports optional search filtering 
    for match history. Redirects to login if no active clan session exists.
    """
    try:
        clan_id = request.session.get('clan_id') #Gotten when an account logs in
        if not clan_id:
            messages.error(request, "Clan session missing.")
            return redirect("login")
        clan = get_object_or_404(Clans, id=clan_id)
        
        clan_stats = get_object_or_404(ClanStats, id=clan_id)
        try:
            match_data = clan_stats.load_match_data_from_file()
        except Exception as e:
            ErrorHandler().handle(e, context="Loading match data")
            match_data = {"matches": []}
        clan.clan_description = mark_safe(markdown.markdown(clan.clan_description))
        form = AddPlayerToClanForm(request.POST or None, clan=clan)
        members =User.objects.filter(profile__clan=clan)
        tournaments = ClanTournament.objects.filter(teams=clan)
        join_requests = ClanJoinRequest.objects.filter(clan=clan, status="pending")
        socials  = make_social_links_dict(ClanSocialLink.objects.filter(clan=clan).all())
        followers = count_followers(clan)
        following = count_following(clan)
    # ============================ get last 5 matches ============================ #
    # Match results
        match_results = []
        if match_data.get("matches"):
            last_5 = match_data["matches"][-5:]
            match_results = [
                "W" if m["result"] == "win"
                else "L" if m["result"] == "loss"
                else "D"
                for m in last_5
            ]
            match_data["matches"] = last_5

        # Search functionality
        query = request.GET.get('q', '').strip().lower()
        if query and match_data.get("matches"):
            match_data["matches"] = [
                m for m in match_data["matches"]
                if any(query in str(m.get(field, '')).lower()
                       for field in ['date', 'tour_name', 'opponent', 'result', 'score'])
            ] 
        context = {
            "clan": clan,
            "stats": clan_stats,
            "players": members,
            "tournaments": tournaments,
            "match_results": match_results,
            "match_data": match_data,
            "join_requests": join_requests,
            "form": form,
            "query": query,
            "followers": followers,
            "following": following,
            'socials': socials,
        }
        return render(request, "clans/clan_dashboard.html", context)

    except Exception as e:
        ErrorHandler().handle(e, context="Clan dashboard view failure")
        messages.error(request, "Something went wrong while loading your dashboard.")
        return redirect("login")

@clan_login_required
@require_POST
def approve_reject(request):
    """
    Handles approval or rejection of a pending clan join request.
    Only accessible by clan admins. Returns a JSON response with the outcome
    or an error message if the request fails validation.
    """
    try:
        request_id = request.POST.get("request_id")
        action = request.POST.get("manage_request")

        if not request_id or action not in ["approve", "reject"]:
            return JsonResponse({"error": "Missing or invalid request parameters."}, status=400)

        join_request = get_object_or_404(ClanJoinRequest, id=request_id)
        #not needed
        player = join_request.player
        clan = join_request.clan
        subject = "Join Request"
        body = f"Welcome to {clan.clan_name}" if action == "approve" else f"Join request declined."

        html_content = render_to_string("clans/member_notify.html", {
            "member_name": player.username,
            "clan_name": clan.clan_name,
            "profile_link":request.build_absolute_uri(f"/clans/{clan.pk}/"),
            "action": "status",
            "status": action
        })

        # Send asynchronously
        threading.Thread(
            target=email_handle.send_email_with_attachment,
            kwargs={
                "subject": subject,
                "body": body,
                "to_email": join_request.player.email,
                "file_path": None,
                "from_email": None,
                "html_content": html_content
            }
        ).start()

        if action == "approve":
            join_request.approve()
            msg = f"{join_request.player.username}'s join request approved."
        else:  
            join_request.reject()
            msg = f"{join_request.player.username}'s join request rejected."
        return JsonResponse({"message": msg})

    except Exception as e:
        ErrorHandler().handle(e, context="Clan join approval/rejection")
        return JsonResponse({"error": "An internal error occurred."}, status=500)

@clan_login_required
@require_POST
def add_remove_players(request):
    """
    Adds or removes players from the current clan.
    Only the clan creator can perform these actions.
    Returns a JSON message with the result or an error.
    """
    try:
        clan = get_object_or_404(Clans, id=request.session['clan_id'])

        form = AddPlayerToClanForm(request.POST or None, clan=clan)
        if request.method == "POST" and form.is_valid():
            action = request.POST.get("action")
            player = form.cleaned_data.get("username")
            profile = get_object_or_404(Profile, user=player)

            if action == "add_player":
                if profile.clan:
                    return JsonResponse({"message": f"{player.username} is already in a clan!"})
                profile.clan = clan
                profile.save()
                return JsonResponse({"message": f"{player.username} has joined"})

            elif action == "remove_player":
                profile.clan = None
                profile.save()
                return JsonResponse({"message": f"{player.username} has been removed from the clan."})

        return JsonResponse({"error": "Invalid request"}, status=400)

    except Exception as e:
        ErrorHandler().handle(e, context='Add/Remove Player in Clan')
        return JsonResponse({"error": "Something went wrong while managing the clan members."}, status=500)

@clan_login_required
def edit_clan_profile(request):
    clan_id = request.session.get('clan_id')
  
    clan = Clans.objects.get(id=clan_id)
    try:
        if request.method == "POST":
            basic_form = ClanBasicInfoForm(request.POST, instance=clan)
            contact_form = ClanContactFormEdit(request.POST, instance=clan)
            media_form = ClanMediaForm(request.POST, request.FILES, instance=clan)
            recruitment_form = ClanRecruitmentForm(request.POST, instance=clan)
            social_formset = ClanSocialLinkFormSet(request.POST, instance=clan)
            pass_form = PasswordChangeForm(request.user, request.POST)

            with transaction.atomic():
                if basic_form.is_valid():
                    basic_form.save()
                if contact_form.is_valid():
                    contact_form.save()
                if media_form.is_valid():
                    media_form.save()
                if recruitment_form.is_valid():
                    recruitment_form.save()
                if social_formset.is_valid():
                    social_formset.save()
                if pass_form.is_valid():
                    user = pass_form.save()
                    update_session_auth_hash(request, user)
                   

            
            forms_status = [
                basic_form.is_valid(),
                contact_form.is_valid(),
                media_form.is_valid(),
                recruitment_form.is_valid(),
                social_formset.is_valid(),pass_form.is_valid()
            ]

            if any(forms_status):
                messages.success(request, "Your changes have been saved.")
                return redirect('edit_clan_profile')
            else:
                messages.error(request, "No changes saved. Please fix the errors.")
                return redirect('clan-home')

        else:
            basic_form = ClanBasicInfoForm(instance=clan)
            contact_form = ClanContactFormEdit(instance=clan)
            media_form = ClanMediaForm(instance=clan)
            recruitment_form = ClanRecruitmentForm(instance=clan)
            social_formset = ClanSocialLinkFormSet(instance=clan)
            pass_form = PasswordChangeForm(request.user)

    except Exception as e:
        messages.error(request, "There was an error updating your clan profile.")
        ErrorHandler().handle(e, context=f"edit_clan_profile view for clan {clan.clan_name}")
        basic_form = ClanBasicInfoForm(instance=clan)
        contact_form = ClanContactFormEdit(instance=clan)
        media_form = ClanMediaForm(instance=clan)
        recruitment_form = ClanRecruitmentForm(instance=clan)
        social_formset = ClanSocialLinkFormSet(instance=clan)
        pass_form = PasswordChangeForm(request.user)

    return render(request, 'clans/edit_clan_profile.html', {
        'basic_form': basic_form,
        'contact_form': contact_form,
        'media_form': media_form,
        'recruitment_form': recruitment_form,
        'social_formset': social_formset,
        'pass_form':pass_form
        
    })

CLAN_FORMS = [
    ("basics", ClanBasicsForm),
    ("contact", ClanContactForm),
    ("media", ClanMediaForm),
    ("extra", ClanExtrasForm),
]

from django.contrib.auth.mixins import LoginRequiredMixin
class ClanRegistrationWizard(LoginRequiredMixin,SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'tmp'))
    form_list = CLAN_FORMS

    def get_form_kwargs(self, step):
        """Pass request.FILES to forms that need file uploads"""
        kwargs = super().get_form_kwargs(step)
        if self.request.method == "POST":
            kwargs.update({'files': self.request.FILES})
        return kwargs

    def get_template_names(self):
        return [f"clans/register/{self.steps.current}.html"]

    def done(self, form_list, **kwargs):
        """Called after all steps are completed and valid."""
        data = self.get_all_cleaned_data()
        try:
            with transaction.atomic():
                clan = Clans(
                    clan_name=data['clan_name'],
                    email=data['email'],
                    clan_tag=data['clan_tag'],
                    clan_description=data['clan_description'],
                    clan_logo=data.get('clan_logo'),
                    clan_profile_pic=data.get('clan_profile_pic'),
                    clan_website=data.get('clan_website'),
                    primary_game=data.get('primary_game'),
                    other_games=data.get('other_games'),
                    country=data.get('country'),
                    created_by=self.request.user,
                    is_recruiting = True
                )
                clan.set_password(data['password'])
                clan.save()
                self.request.session['pending_verification'] = clan.email or clan.clan_name
                self.request.session['pending_model'] = 'clan'  # Store model type for verification
                profile = self.request.user.profile
                profile.clan = clan
                profile.save()

                Thread(
                    target=verify.send_verification,
                    kwargs={"account": clan, "model_type": "clan", "method": "email"}
                ).start()

            messages.info(self.request, "We've sent you a verification email.")
            return redirect("verification_pending")
        except Exception as e:
            ErrorHandler().handle(e, context="clan_register_wizard")
            messages.error(self.request, "Something went wrong during registration.")
            return redirect("clan_register")


