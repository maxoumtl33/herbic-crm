from django.contrib import admin
from .models import Produit, CategorieProduit, RecommandationProduit


@admin.register(CategorieProduit)
class CategorieProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_categorie')
    list_filter = ('type_categorie',)


class RecommandationInline(admin.TabularInline):
    model = RecommandationProduit
    extra = 0


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'categorie', 'format_produit', 'prix_unitaire', 'en_stock')
    list_filter = ('categorie', 'en_stock')
    search_fields = ('code', 'nom')
    inlines = [RecommandationInline]
