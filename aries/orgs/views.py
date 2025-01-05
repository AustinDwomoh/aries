from django.shortcuts import render

# Create your views here.
def organisation(request):
    return render(request, 'orgs/organisations.html')