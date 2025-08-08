from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.models import User
from clans.models import Clans
from aries.settings import ErrorHandler
from scripts.follow import *
from django.views.generic import ListView
from .models import Follow
from django.contrib.contenttypes.models import ContentType

def home(request):
    """
    Renders the home page of the website.

    Args:
        request (HttpRequest): The HTTP request object sent by the client.

    Returns:
        HttpResponse: Renders the 'Home/index.html' template as the response.
    """
    try:
        clans = Clans.objects.select_related('stat').filter(is_verified=True).order_by('-stat__elo_rating')[:10]
        players = User.objects.all().order_by('-profile__stats__elo_rating')[:10]
        context ={
            "players":players,
            "clans":clans
        }
    except Exception as e:
        ErrorHandler().handle(e, context="Home Page")
        context = {
            "players": [],
            "clans": []}
        
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


def trigger_error_view(request):
    handler = ErrorHandler()

    try:
        # Intentional error
        1 / 0
    except Exception as e:
        handler.handle(e, context="Trigger error test view")
        return HttpResponse("Error has been logged and admin notified.", status=500)

def follow_list_view(request, ftype, model, profile_id):
    if ftype == 'followers':
        instance = get_followed_instance(model, profile_id)
        data = get_followers(instance)  
    elif ftype == 'following':
        instance = get_followed_instance(model, profile_id)
        data = get_following(instance)  
    else:
        return HttpResponseBadRequest("Invalid follow type.")

    context = {
        "users": data.get("users", []),
        "clans": data.get("clans", []),
        "view_type": ftype,
        "profile_id": profile_id,
    }
    return render(request, "Home/follow_list.html", context)


    
