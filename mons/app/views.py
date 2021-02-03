from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template('app/index.html')
    return HttpResponse(template.render({}, request))


def profile(request):
    template = loader.get_template('app/profile.html')
    return HttpResponse(template.render({}, request))


def preferences(request):
    template = loader.get_template('app/preferences.html')
    return HttpResponse(template.render({}, request))


def destination(request):
    template = loader.get_template('app/newDestination.html')
    return HttpResponse(template.render({}, request))
