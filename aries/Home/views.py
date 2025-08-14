from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.models import User
from clans.models import Clans
from scripts.error_handle import ErrorHandler
from scripts.follow import *


def home(request):
    """
    Renders the home page of the website.
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
    """
    return render(request, 'Home/about.html')

def trigger_error_view(request):
    """
    A test view that deliberately raises an exception (division by zero) to
    verify error handling and logging mechanisms. The error is caught, logged,
    and a 500 response is returned to confirm the error was recorded.
    """
    try:
        # Intentional error
        1 / 0
    except Exception as e:
        ErrorHandler().handle(e, context="Trigger error test view")
        return HttpResponse("Error has been logged and admin notified.", status=500)

def follow_list_view(request, ftype, model, profile_id):
    """
    Displays a list of followers or following entities for a given profile.

    Args:
        ftype (str): The type of list to display, either 'followers' or 'following'.
        model (str): The model name of the profile entity.
        profile_id (int): The ID of the profile whose followers/following to retrieve.

    Returns:
        Rendered HTML page showing the lists of users and clans for the specified type.

    Handles invalid 'ftype' with a bad request response.
    """
    print(f"Follow list view called with ftype={ftype}, model={model}, profile_id={profile_id}")
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


    
