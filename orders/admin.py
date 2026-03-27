from django.contrib import admin
from .models import Commande, LigneCommande


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ('prepare', 'prepare_par', 'date_preparation')


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'client', 'vendeur', 'statut', 'date_commande')
    list_filter = ('statut', 'date_commande')
    search_fields = ('client__nom_ferme', 'client__code')
    inlines = [LigneCommandeInline]
