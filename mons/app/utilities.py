import math
import json
from django.contrib.staticfiles import finders

def distance(lat1, lon1, lat2, lon2):
    if (lat1 == lat2) and (lon1 == lon2):
        return 0
    else:
        theta = lon1-lon2
        dist = math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(theta))
        dist = math.acos(dist)
        dist = math.degrees(dist)
        miles = dist * 60 * 1.1515;

        return miles * 1.609344


def get_near_cambio_stations(lat, lng, radius = 2):
    near_id = []
    f = open(finders.find('data/cambios-stations.json'), 'r')
    infos = f.read().encode('utf-8')
    results = json.loads(infos)
    f.close()

    for station in results:
        camb_lat = station['geoposition']['latitude']
        camb_lng = station['geoposition']['longitude']

        if distance(lat, lng, camb_lat, camb_lng) <= radius:
            near_id.append(station['id'])
    return near_id


def get_cambio_by_id(cambio_id):
    f = open(finders.find('data/cambios-stations.json'), 'r')
    infos = f.read().encode('utf-8')
    results = json.loads(infos)
    f.close()

    for station in results:
        if station['id'] == cambio_id:
            return station
    return None


def get_cambio_distance(lat, lon, id):
    f = open(finders.find('data/cambios-stations.json'), 'r')
    infos = f.read().encode('utf-8')
    results = json.loads(infos)
    f.close()

    for station in results:
        if station['id'] == id:
            return distance(lat, lon, station['geoposition']['latitude'], station['geoposition']['longitude'])
    return 0


def get_close_stations(lat, lon, radius = 2):
    f = open(finders.find('data/gares-sncb.json'), 'r')
    infos = f.read()
    results = json.loads(infos)
    f.close()

    final_gares = []

    for station in results:
        gare_lat = float(station['fields']['latitude'])
        gare_lng = float(station['fields']['longitude'])
        
        dist = distance(lat, lon, gare_lat, gare_lng)
        if dist < radius:
            final_gares.append({
                'gare_id': station['fields']['id'],
                'gare_name': station['fields']['name'],
                'distance': dist
            })
    return final_gares
