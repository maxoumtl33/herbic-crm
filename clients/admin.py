from django.contrib import admin
from .models import Client, Culture, ProduitArrosage


class CultureInline(admin.TabularInline):
    model = Culture
    extra = 0


class ProduitArrosageInline(admin.TabularInline):
    model = ProduitArrosage
    extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom_ferme', 'prenom', 'nom', 'ville', 'vendeur')
    list_filter = ('ville', 'vendeur')
    search_fields = ('code', 'nom_ferme', 'nom', 'prenom')
    inlines = [CultureInline]


@admin.register(Culture)
class CultureAdmin(admin.ModelAdmin):
    list_display = ('client', 'type_culture', 'superficie_acres', 'semence', 'annee')
    list_filter = ('type_culture', 'annee')
    inlines = [ProduitArrosageInline]
