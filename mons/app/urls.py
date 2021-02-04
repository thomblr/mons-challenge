from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="index"),
    path('profile/', views.profile, name="profile"),
    path('preferences/', views.preferences, name="preferences"),
    path('destination/', views.destination, name="destination"),
    path('trajets/', views.trajets, name="trajets"),
    path('parcours/<slug:slug>', views.parcours, name="parcours"),
]