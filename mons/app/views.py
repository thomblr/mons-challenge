from django.http.response import HttpResponseRedirect
from .models import SaveTripPoints, UserSettings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from opencage.geocoder import OpenCageGeocode

from .forms import AccueilDestinationForm, NewDestinationForm, SaveSettingsForm
from .utilities import distance, get_cambio_by_id, get_near_cambio_stations, get_cambio_distance, get_close_stations
from django.contrib.staticfiles import finders


def index(request):
    form = AccueilDestinationForm()
    template = loader.get_template('app/index.html')
    return HttpResponse(template.render({'form': form}, request))


@login_required
def profile(request):
    template = loader.get_template('app/profile.html')

    user = request.user.username

    try:
        pts = SaveTripPoints.objects.get(user = request.user)
    except Exception:
        pts = 0

    context = {
        'username': user,
        'pts': pts
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

        results_start = geocoder.geocode(depart)
        results_end = geocoder.geocode(end)

        lat = results_start[0]['geometry']['lat']
        lng = results_start[0]['geometry']['lng']

        close_gares = get_close_stations(lat, lng)

        cambios = []
        cars = get_near_cambio_stations(results_start[0]['geometry']['lat'], results_start[0]['geometry']['lng'])

        for car in cars:
            dist = get_cambio_distance(results_start[0]['geometry']['lat'], results_start[0]['geometry']['lng'], car)
            cambios.append({
                'car_id': car,
                'car_name': get_cambio_by_id(car)['displayName'],
                'car_dist': dist
            })

        distance_km = distance(
            results_start[0]['geometry']['lat'],
            results_start[0]['geometry']['lng'],
            results_end[0]['geometry']['lat'],
            results_end[0]['geometry']['lng'])

        duration_trajet_pieds = (1/4.7) * distance_km
        duration_trajet_car = (1/60) * distance_km

        context = {
            'duration_foot': duration_trajet_pieds,
            'duration_car': duration_trajet_car,
            'cambios': cambios,
            'gares': close_gares
        }

        template = loader.get_template('app/trajets.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/destination/')


def parcours(request):
    template = loader.get_template('app/parcours.html')
    return HttpResponse(template.render({}, request))