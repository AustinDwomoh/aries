from django.shortcuts import render

# Create your views here.
def clubs(request):
    return render(request, 'clubs/clubs.html')