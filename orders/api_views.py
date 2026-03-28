"""API JSON pour la recherche dynamique."""
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from products.models import Produit, CategorieProduit
from clients.models import Client


@login_required
def api_produits(request):
    """Recherche de produits en JSON."""
    q = request.GET.get('q', '')
    categorie = request.GET.get('categorie', '')
    produits = Produit.objects.filter(en_stock=True).select_related('categorie')

    if q:
        produits = produits.filter(
            Q(nom__icontains=q) | Q(code__icontains=q) | Q(description__icontains=q)
        )
    if categorie:
        produits = produits.filter(categorie__type_categorie=categorie)

    data = [{
        'id': p.pk,
        'code': p.code,
        'nom': p.nom,
        'categorie': str(p.categorie),
        'type_categorie': p.categorie.type_categorie,
        'format': p.format_produit,
        'prix': float(p.prix_unitaire) if p.prix_unitaire else None,
    } for p in produits[:50]]

    return JsonResponse({'produits': data})


@login_required
def api_clients(request):
    """Recherche de clients en JSON."""
    q = request.GET.get('q', '')
    clients = Client.objects.all()

    if request.user.is_vendeur():
        clients = clients.filter(vendeur=request.user)

    if q:
        clients = clients.filter(
            Q(nom__icontains=q) | Q(prenom__icontains=q) |
            Q(nom_ferme__icontains=q) | Q(code__icontains=q) |
            Q(ville__icontains=q)
        )

    data = [{
        'id': c.pk,
        'code': c.code,
        'nom_ferme': c.nom_ferme,
        'nom': f'{c.prenom} {c.nom}',
        'ville': c.ville,
    } for c in clients[:30]]

    return JsonResponse({'clients': data})
