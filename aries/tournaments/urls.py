from django.urls import path
from . import views

urlpatterns = [
    path('', views.tours, name='tournament-home'),
]
