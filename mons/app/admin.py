from django.contrib import admin

from .models import UserSettings, SaveTripPoints

# Register your models here.
admin.site.register([UserSettings, SaveTripPoints])