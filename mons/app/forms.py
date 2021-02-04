from django import forms
from django.contrib.admin.widgets import AdminTimeWidget

class SaveSettingsForm(forms.Form):
    CHOICES_category = [
        ('travailleur', 'Travailleur'),
        ('student', 'Etudiant'),
        ('parent', "Parent d'élève")
    ]

    CHOICES_langue = [
        ('french', 'Français'),
        ('english', 'English'),
        ('nederlands', "Nederlands")
    ]

    home = forms.CharField(label="Adresse du domicile")
    category = forms.ChoiceField(choices=CHOICES_category, widget=forms.RadioSelect, label="Catégorie d'utilisateur")
    langue = forms.ChoiceField(choices=CHOICES_langue, widget=forms.RadioSelect, label="Langue")


class NewDestinationForm(forms.Form):
    depart = forms.CharField(label="Départ")
    time = forms.TimeField(label="à")
    destination = forms.CharField(label="Destination")

    CHOICES_trip = [
        ('short', 'Le plus court'),
        ('fast', 'Le plus rapide'),
        ('eco', 'Le plus écologique')
    ]

    trip = forms.ChoiceField(choices=CHOICES_trip, widget=forms.RadioSelect)


class AccueilDestinationForm(forms.Form):
    address = forms.CharField()
    save = forms.BooleanField(label="Enregistrer mon trajet", required=False)