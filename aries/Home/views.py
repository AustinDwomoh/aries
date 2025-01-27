from django.shortcuts import render

def home(request):
    """
    Renders the home page of the website.

    Args:
        request (HttpRequest): The HTTP request object sent by the client.

    Returns:
        HttpResponse: Renders the 'Home/index.html' template as the response.
    """
    return render(request, 'Home/index.html')


def about(request):
    """
    Renders the about page of the website.

    Args:
        request (HttpRequest): The HTTP request object sent by the client.

    Returns:
        HttpResponse: Renders the 'Home/about.html' template as the response.
    """
    return render(request, 'Home/about.html')