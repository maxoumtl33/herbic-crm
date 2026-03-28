"""Rapports d'analyse vendeurs pour le directeur."""
from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from .decorators import directeur_required
from .models import User
from orders.models import Commande
from clients.models import Client, Culture


def _parse_dates(request):
    """Parse les dates de filtre depuis la requête."""
    periode = request.GET.get('periode', 'mois')
    today = date.today()

    if periode == 'jour':
        debut = today
        fin = today
    elif periode == 'semaine':
        debut = today - timedelta(days=today.weekday())
        fin = today
    elif periode == 'mois':
        debut = today.replace(day=1)
        fin = today
    elif periode == 'annee':
        debut = today.replace(month=1, day=1)
        fin = today
    elif periode == 'custom':
        try:
            debut = date.fromisoformat(request.GET.get('debut', ''))
            fin = date.fromisoformat(request.GET.get('fin', ''))
        except (ValueError, TypeError):
            debut = today.replace(day=1)
            fin = today
    else:
        debut = today.replace(day=1)
        fin = today

    return periode, debut, fin


def _stats_vendeur(vendeur, debut, fin):
    """Calcule les stats d'un vendeur pour une période."""
    commandes = vendeur.commandes_vendeur.filter(
        date_commande__date__gte=debut,
        date_commande__date__lte=fin,
    ).select_related('client')

    commandes_livrees = commandes.filter(statut='livree')
    ca = sum((c.total for c in commandes_livrees), Decimal('0'))

    clients = vendeur.clients_assignes.all()
    nb_cultures = Culture.objects.filter(client__vendeur=vendeur).count()

    # Top clients par CA
    client_ca = {}
    for cmd in commandes_livrees:
        nom = cmd.client.nom_ferme
        client_ca[nom] = client_ca.get(nom, Decimal('0')) + cmd.total
    top_clients = sorted(client_ca.items(), key=lambda x: x[1], reverse=True)[:5]

    # Commandes par statut
    par_statut = {}
    for cmd in commandes:
        label = cmd.get_statut_display()
        par_statut[label] = par_statut.get(label, 0) + 1

    # Produits les plus vendus
    produit_qty = {}
    for cmd in commandes_livrees:
        for ligne in cmd.lignes.select_related('produit').all():
            nom = ligne.produit.nom
            produit_qty[nom] = produit_qty.get(nom, 0) + int(ligne.quantite)
    top_produits = sorted(produit_qty.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        'vendeur': vendeur,
        'nb_commandes': commandes.count(),
        'nb_livrees': commandes_livrees.count(),
        'ca': ca,
        'nb_clients': clients.count(),
        'nb_cultures': nb_cultures,
        'top_clients': top_clients,
        'par_statut': par_statut,
        'top_produits': top_produits,
    }


@directeur_required
def rapport_vendeurs(request):
    periode, debut, fin = _parse_dates(request)
    vendeur_id = request.GET.get('vendeur', '')

    vendeurs = User.objects.filter(role='vendeur', is_active=True)

    if vendeur_id:
        # Rapport détaillé pour un vendeur
        vendeur = get_object_or_404(User, pk=vendeur_id, role='vendeur')
        stats = _stats_vendeur(vendeur, debut, fin)

        # Commandes détaillées
        commandes = vendeur.commandes_vendeur.filter(
            date_commande__date__gte=debut,
            date_commande__date__lte=fin,
        ).select_related('client').order_by('-date_commande')

        return render(request, 'accounts/rapport_vendeur_detail.html', {
            'stats': stats,
            'commandes': commandes,
            'vendeurs': vendeurs,
            'vendeur_id': vendeur_id,
            'periode': periode,
            'debut': debut,
            'fin': fin,
        })
    else:
        # Vue globale tous vendeurs
        all_stats = []
        total_ca = Decimal('0')
        total_commandes = 0
        total_livrees = 0

        for v in vendeurs:
            s = _stats_vendeur(v, debut, fin)
            all_stats.append(s)
            total_ca += s['ca']
            total_commandes += s['nb_commandes']
            total_livrees += s['nb_livrees']

        all_stats.sort(key=lambda x: x['ca'], reverse=True)

        return render(request, 'accounts/rapport_vendeurs.html', {
            'all_stats': all_stats,
            'vendeurs': vendeurs,
            'vendeur_id': vendeur_id,
            'periode': periode,
            'debut': debut,
            'fin': fin,
            'total_ca': total_ca,
            'total_commandes': total_commandes,
            'total_livrees': total_livrees,
        })
