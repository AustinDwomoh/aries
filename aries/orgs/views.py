from django.shortcuts import render

def organisation(request):
    return render(request, 'orgs/organisations.html')