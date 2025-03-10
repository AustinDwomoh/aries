from django.shortcuts import render
from django.contrib.auth.models import User
from clubs.models import Clans
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Follow, User


def home(request):
    """
    Renders the home page of the website.

    Args:
        request (HttpRequest): The HTTP request object sent by the client.

    Returns:
        HttpResponse: Renders the 'Home/index.html' template as the response.
    """
    clans = Clans.objects.all().order_by('-stat__elo_rating')[:10] 
    players = User.objects.all().order_by('-profile__stats__elo_rating')[:10]
    context ={
        "players":players,
        "clans":clans
    }
    
    return render(request, 'Home/index.html',context)


def about(request):
    """
    Renders the about page of the website.

    Args:
        request (HttpRequest): The HTTP request object sent by the client.

    Returns:
        HttpResponse: Renders the 'Home/about.html' template as the response.
    """
    return render(request, 'Home/about.html')



@login_required
def follow_user(request, user_id):
    """Allows a user to follow another user."""
    user_to_follow = get_object_or_404(User, id=user_id)
    follow, created = Follow.objects.get_or_create(follower=request.user, following_user=user_to_follow)
    if created:
        return JsonResponse({"message": f"You are now following {user_to_follow.username}"})
    return JsonResponse({"message": "You are already following this user."})

@login_required
def unfollow_user(request, user_id):
    """Allows a user to unfollow another user."""
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following_user=user_to_unfollow).delete()
    return JsonResponse({"message": f"You have unfollowed {user_to_unfollow.username}"})

@login_required
def follow_club(request, club_id):
    """Allows a user to follow a club."""
    club_to_follow = get_object_or_404(Clans, id=club_id)
    follow, created = Follow.objects.get_or_create(follower=request.user, following_club=club_to_follow)
    if created:
        return JsonResponse({"message": f"You are now following {club_to_follow.clan_name}"})
    return JsonResponse({"message": "You are already following this club."})

@login_required
def unfollow_club(request, club_id):
    """Allows a user to unfollow a club."""
    club_to_unfollow = get_object_or_404(Clans, id=club_id)
    Follow.objects.filter(follower=request.user, following_club=club_to_unfollow).delete()
    return JsonResponse({"message": f"You have unfollowed {club_to_unfollow.clan_name}"})
