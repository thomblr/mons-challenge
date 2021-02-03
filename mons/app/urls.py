from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('profile/', views.profile, name="profile"),
    path('preferences/', views.preferences, name="preferences"),
    path('destination/', views.destination, name="destination"),
]