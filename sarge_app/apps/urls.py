from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('apps/about/', views.about, name='about'),
    path('apps/clubs/', views.clubs, name='clubs'),
    path('apps/members/', views.members, name='members'),
    path('apps/tournament/', views.tournament, name='tournament'),
]