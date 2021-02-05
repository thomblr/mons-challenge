from django.http.response import HttpResponseRedirect
from .models import SaveTripPoints, UserSettings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from opencage.geocoder import OpenCageGeocode
import datetime

from .forms import AccueilDestinationForm, NewDestinationForm, SaveSettingsForm
from .utilities import distance, get_near_cambio_stations, get_close_stations
from django.contrib.staticfiles import finders


def index(request):
    form = AccueilDestinationForm()
    template = loader.get_template('app/index.html')
    return HttpResponse(template.render({'form': form}, request))


@login_required
def profile(request):
    template = loader.get_template('app/profile.html')

    user = request.user.username

    context = {
        'username': user
    }

    return HttpResponse(template.render(context, request))


@login_required
def preferences(request):
    if request.method == 'POST':
        form = SaveSettingsForm(request.POST)
        if form.is_valid():
            home = form.cleaned_data.get('home')
            category = form.cleaned_data.get('category')
            langue = form.cleaned_data.get('langue')
            settings = UserSettings(home=home, category=category, langue=langue, user=request.user)
            settings.save()
        template = loader.get_template('app/preferences.html')
        return HttpResponse(template.render({'form': form}, request))
    else:
        try:
            user = UserSettings.objects.get(user=request.user)
            form = SaveSettingsForm({
                'home': user.home,
                'category': user.category,
                'langue': user.langue
            })
        except UserSettings.DoesNotExist:
            form = SaveSettingsForm()

        template = loader.get_template('app/preferences.html')
        return HttpResponse(template.render({'form': form}, request))


def destination(request):
    try:
        start = UserSettings.objects.get(user=request.user).home
    except UserSettings.DoesNotExist:
        start = ""

    end = ""
    if request.method == 'POST':
        req_form = AccueilDestinationForm(request.POST)
        if req_form.is_valid():
            end = req_form.cleaned_data.get("address")

    form = NewDestinationForm({
        'depart': start,
        'destination': end,
        'time': '08:00',
        'trip': 'short'
    })
    template = loader.get_template('app/newDestination.html')
    return HttpResponse(template.render({'form': form}, request))


def trajets(request):
    API_KEY = "bfc43659b2884e7a84e2e2c9967126c4"
    geocoder = OpenCageGeocode(API_KEY)

    if request.method == 'POST':
        depart = request.POST['depart'] + " BELGIQUE"
        end = request.POST['destination'] + " BELGIQUE"
        trip_type = request.POST['trip']

        time = request.POST['time']
        time_obj = datetime.datetime.strptime(time, '%H:%S')

        busy_hours = False
        first_hour = datetime.time(7, 30)
        second_hour = datetime.time(9, 0)
        if time_obj.time() <= second_hour and time_obj.time() >= first_hour:
            busy_hours = True
        
        third_hour = datetime.time(16, 00)
        fourth_hour = datetime.time(18, 00)
        if time_obj.time() <= fourth_hour and time_obj.time() >= third_hour:
            busy_hours = True

        results_start = geocoder.geocode(depart)
        results_end = geocoder.geocode(end)

        lat = results_start[0]['geometry']['lat']
        lng = results_start[0]['geometry']['lng']

        gare = False
        close_gares = get_close_stations(lat, lng)
        if len(close_gares) > 0:
            gare = True

        rent_car = False
        cars = get_near_cambio_stations(lat, lng)

        if len(cars) > 0:
            rent_car = True

        bus = False
        # all_bus = get_close_bus_station(lat, lng)
        # if len(all_bus) > 0:
        #     bus = True

        distance_km = distance(
            results_start[0]['geometry']['lat'],
            results_start[0]['geometry']['lng'],
            results_end[0]['geometry']['lat'],
            results_end[0]['geometry']['lng']
        )

        duration_trajet_pieds = (1/4.7) * distance_km
        duration_trajet_car = (1/50) * distance_km
        duration_trajet_car *= 60
        if busy_hours:
            duration_trajet_car += 25
        duration_trajet_bike = (1/15) * distance_km

        context = {
            'gare': gare,
            'rent_car': rent_car,
            'bus': bus,
            'duration_trip': {
                'foot': duration_trajet_pieds * 60 + 5,
                'car': duration_trajet_car + 2,
                'bike': duration_trajet_bike * 60 + 10,
            },
            'busy_hours': busy_hours,
            'eco': True if trip_type == 'eco' else False
        }

        request.session['current_search'] = {
            'start_location': {
                'address': request.POST['depart'],
                'latitude': lat,
                'longitude': lng
            },
            'end_location': {
                'latitude': results_end[0]['geometry']['lat'],
                'longitude': results_end[0]['geometry']['lng'],
                'address': request.POST['destination']
            },
            'distance': distance_km
        }

        template = loader.get_template('app/trajets.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/destination/')


def parcours(request, transport):
    transport_types = ['car', 'walk', 'train', 'bus', 'taxi', 'cycling']

    co_conso = {
        'car': 157,
        'walk': 0,
        'train': 0,
        'bus': 70/98,
        'taxi': 150/4,
        'cycling': 0
    }

    if transport in transport_types:
        current_search = request.session.get('current_search', {})
        current_search['conso'] = co_conso[transport]
        request.session['trajet_type'] = transport
        template = loader.get_template('app/parcours.html')
        return HttpResponse(template.render(current_search, request))
    else:
        return HttpResponseRedirect('/')


@login_required
def points(request):
    try:
        infos = list(SaveTripPoints.objects.all().filter(user = request.user).values())
        pts = SaveTripPoints.objects.all().filter(user = request.user).filter(statut='Validé').aggregate(Sum('pts'))
    except SaveTripPoints.DoesNotExist:
        pts = 0
        infos = {}

    context = {
        'username': request.user.username,
        'pts': pts['pts__sum'],
        'infos': infos,
    }

    template = loader.get_template('app/points.html')
    return HttpResponse(template.render(context, request))


@login_required
def parcours_validation(request):
    transport_types = {
        'car': {
            'pts': 0,
            'display': "Voiture"
        }, 
        'walk': {
            'pts': 3,
            'display': "Marche"
        }, 
        'train': {
            'pts': 2,
            'display': "Train"
        }, 
        'bus': {
            'pts': 2,
            'display': "Bus"
        }, 
        'taxi': {
            'pts': 1,
            'display': "Voiture de location"
        }, 
        'cycling': {
            'pts': 3,
            'display': "Vélo"
        }
    }

    infos = request.session.get('trajet_type', {})
    pts = transport_types[infos]['pts']
    display_name = transport_types[infos]['display']
    new_points = SaveTripPoints(user=request.user, trajet=display_name, pts=pts, statut='En attente')
    new_points.save()
    return HttpResponseRedirect('/')


def rgpd(request):
    template = loader.get_template('app/rgpd.html')
    return HttpResponse(template.render({}, request))