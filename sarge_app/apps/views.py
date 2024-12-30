from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse


def about(request):
    template = loader.get_template('aboutUs.html')
    return HttpResponse(template.render())
def clubs(request):
    template = loader.get_template('clubs.html')
    return HttpResponse(template.render())

def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())

def members(request):
    template = loader.get_template('members.html')
    return HttpResponse(template.render())

def tournament(request):
    template = loader.get_template("tournament.html")
    return HttpResponse(template.render())

