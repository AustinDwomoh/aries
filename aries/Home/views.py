from django.shortcuts import render
from django.contrib.auth.models import User
from clubs.models import Clans


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