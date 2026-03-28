"""Page de statistiques globales pour vendeur et directeur."""
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Sum, Q
from accounts.decorators import staff_required
from accounts.models import User
from orders.models import Commande, LigneCommande
from clients.models import Client, Culture
from products.models import Produit


@staff_required
def page_statistiques(request):
    user = request.user
    annee = timezone.now().year
    client_id = request.GET.get('client', '')

    # === PRODUITS LES PLUS VENDUS ===
    lignes_qs = LigneCommande.objects.filter(
        commande__statut='livree',
        commande__date_commande__year=annee,
    ).select_related('produit', 'produit__categorie')

    if user.is_vendeur():
        lignes_qs = lignes_qs.filter(commande__vendeur=user)

    # Agréger par produit
    produit_stats = {}
    for ligne in lignes_qs:
        pk = ligne.produit.pk
        if pk not in produit_stats:
            produit_stats[pk] = {
                'produit': ligne.produit,
                'quantite': 0,
                'ca': Decimal('0'),
                'nb_commandes': set(),
            }
        produit_stats[pk]['quantite'] += int(ligne.quantite)
        if ligne.sous_total:
            produit_stats[pk]['ca'] += ligne.sous_total
        produit_stats[pk]['nb_commandes'].add(ligne.commande_id)

    # Convertir les sets en counts
    for p in produit_stats.values():
        p['nb_commandes'] = len(p['nb_commandes'])

    top_produits_qty = sorted(produit_stats.values(), key=lambda x: x['quantite'], reverse=True)[:10]
    top_produits_ca = sorted(produit_stats.values(), key=lambda x: x['ca'], reverse=True)[:10]

    # === CLASSEMENT VENDEURS (directeur uniquement) ===
    vendeur_stats = []
    # Classement vendeurs visible par vendeur ET directeur
    if user.is_directeur() or user.is_vendeur():
        for v in User.objects.filter(role='vendeur', is_active=True):
            cmds = v.commandes_vendeur.filter(statut='livree', date_commande__year=annee)
            ca = sum((c.total for c in cmds), Decimal('0'))
            vendeur_stats.append({
                'vendeur': v,
                'ca': ca,
                'nb_commandes': cmds.count(),
                'nb_clients': v.clients_assignes.count(),
                'nb_cultures': Culture.objects.filter(client__vendeur=v).count(),
            })
        vendeur_stats.sort(key=lambda x: x['ca'], reverse=True)

    # === STATS PAR CLIENT ===
    clients_qs = Client.objects.all()
    if user.is_vendeur():
        clients_qs = clients_qs.filter(vendeur=user)

    client_detail = None
    if client_id:
        try:
            client_obj = clients_qs.get(pk=client_id)
            cmds = client_obj.commandes.filter(statut='livree', date_commande__year=annee)
            ca_client = sum((c.total for c in cmds), Decimal('0'))

            # Produits achetés par ce client
            lignes_client = LigneCommande.objects.filter(
                commande__client=client_obj,
                commande__statut='livree',
                commande__date_commande__year=annee,
            ).select_related('produit', 'produit__categorie')

            produits_client = {}
            for l in lignes_client:
                pk = l.produit.pk
                if pk not in produits_client:
                    produits_client[pk] = {
                        'produit': l.produit,
                        'quantite': 0,
                        'ca': Decimal('0'),
                    }
                produits_client[pk]['quantite'] += int(l.quantite)
                if l.sous_total:
                    produits_client[pk]['ca'] += l.sous_total

            top_produits_client = sorted(produits_client.values(), key=lambda x: x['ca'], reverse=True)

            # Catégories achetées
            cat_stats = {}
            for p in produits_client.values():
                cat = str(p['produit'].categorie)
                cat_stats[cat] = cat_stats.get(cat, Decimal('0')) + p['ca']
            top_categories = sorted(cat_stats.items(), key=lambda x: x[1], reverse=True)

            client_detail = {
                'client': client_obj,
                'ca': ca_client,
                'nb_commandes': cmds.count(),
                'nb_cultures': client_obj.cultures.count(),
                'top_produits': top_produits_client,
                'top_categories': top_categories,
            }
        except Client.DoesNotExist:
            pass

    # === STATS GLOBALES ===
    commandes_annee = Commande.objects.filter(date_commande__year=annee)
    if user.is_vendeur():
        commandes_annee = commandes_annee.filter(vendeur=user)

    ca_total = sum(
        (c.total for c in commandes_annee.filter(statut='livree')),
        Decimal('0'),
    )

    # Top catégories globales
    cat_globale = {}
    for p in produit_stats.values():
        cat = str(p['produit'].categorie)
        cat_globale[cat] = cat_globale.get(cat, Decimal('0')) + p['ca']
    top_categories_globale = sorted(cat_globale.items(), key=lambda x: x[1], reverse=True)

    return render(request, 'accounts/statistiques.html', {
        'annee': annee,
        'ca_total': ca_total,
        'nb_commandes': commandes_annee.count(),
        'nb_livrees': commandes_annee.filter(statut='livree').count(),
        'top_produits_qty': top_produits_qty,
        'top_produits_ca': top_produits_ca,
        'top_categories_globale': top_categories_globale,
        'vendeur_stats': vendeur_stats,
        'clients_list': clients_qs.order_by('nom_ferme'),
        'client_id': client_id,
        'client_detail': client_detail,
    })
