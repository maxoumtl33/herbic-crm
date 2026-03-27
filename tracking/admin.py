from django.contrib import admin
from .models import SuiviPousse, StatistiqueCulture


@admin.register(SuiviPousse)
class SuiviPousseAdmin(admin.ModelAdmin):
    list_display = ('culture', 'date_observation', 'stade_croissance', 'etat_general', 'observateur')
    list_filter = ('etat_general', 'date_observation')


@admin.register(StatistiqueCulture)
class StatistiqueCultureAdmin(admin.ModelAdmin):
    list_display = ('culture', 'rendement_estime', 'rendement_reel', 'taux_germination')
