"""API JSON pour la recherche dynamique."""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from products.models import Produit, CategorieProduit
from clients.models import Client
from orders.models import Commande


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
        'stock': p.quantite_stock,
        'seuil': p.seuil_alerte_stock,
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


@login_required
def api_recherche_globale(request):
    """Recherche dans clients, produits et commandes en une seule requête."""
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'clients': [], 'produits': [], 'commandes': []})

    # Clients
    clients_qs = Client.objects.filter(
        Q(nom__icontains=q) | Q(prenom__icontains=q) |
        Q(nom_ferme__icontains=q) | Q(code__icontains=q)
    )
    if request.user.is_vendeur():
        clients_qs = clients_qs.filter(vendeur=request.user)
    clients = [{'id': c.pk, 'nom_ferme': c.nom_ferme, 'nom': f'{c.prenom} {c.nom}',
                'type': 'client'} for c in clients_qs[:5]]

    # Produits
    produits_qs = Produit.objects.filter(
        Q(nom__icontains=q) | Q(code__icontains=q)
    )[:5]
    produits = [{'id': p.pk, 'nom': p.nom, 'code': p.code, 'type': 'produit'} for p in produits_qs]

    # Commandes
    commandes_qs = Commande.objects.filter(
        Q(client__nom_ferme__icontains=q) | Q(pk__icontains=q if q.isdigit() else 0)
    )
    if request.user.is_vendeur():
        commandes_qs = commandes_qs.filter(vendeur=request.user)
    commandes = [{'id': c.pk, 'numero': f'CMD-{c.pk:05d}', 'client': c.client.nom_ferme,
                  'statut': c.get_statut_display(), 'type': 'commande'}
                 for c in commandes_qs.select_related('client')[:5]]

    return JsonResponse({'clients': clients, 'produits': produits, 'commandes': commandes})
