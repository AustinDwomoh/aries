from django.shortcuts import render

# Create your views here.
def tours(request):
    return render(request,'tournaments/tours.html')