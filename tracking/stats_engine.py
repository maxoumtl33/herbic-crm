"""
Moteur de calcul automatique des statistiques de culture.
"""
from decimal import Decimal
from django.db.models import Q
from products.models import Produit


def calculer_stats_auto(culture):
    """
    Calcule les statistiques automatiques pour une culture.
    Retourne un dict avec les valeurs calculées.
    """
    stats = {}

    # 1. Taux de germination = population réelle / population visée × 100
    if culture.population_visee and culture.population_reelle:
        stats['taux_germination'] = round(
            (culture.population_reelle / culture.population_visee) * 100, 1
        )

    # 2. Coût total intrants = somme des produits d'arrosage
    #    Essaie de matcher le produit d'arrosage avec le catalogue pour le prix
    cout_total = Decimal('0')
    has_any_cost = False
    for pa in culture.produits_arrosage.all():
        # Chercher le produit dans le catalogue par nom
        produit = Produit.objects.filter(
            Q(nom__icontains=pa.nom_produit) | Q(nom_produit_match=pa.nom_produit)
        ).first() if False else None  # Skip la recherche complexe

        # Méthode simple: chercher par nom partiel
        produits = Produit.objects.filter(nom__icontains=pa.nom_produit.split()[0])
        if produits.exists():
            produit = produits.first()
            if produit.prix_unitaire and pa.quantite_totale:
                # Estimer le nombre d'unités à partir de la quantité totale et la contenance
                if produit.contenance_valeur:
                    nb_unites = pa.quantite_totale / produit.contenance_valeur
                    cout_ligne = nb_unites * produit.prix_unitaire
                else:
                    cout_ligne = pa.quantite_totale * produit.prix_unitaire
                cout_total += cout_ligne
                has_any_cost = True

    if has_any_cost:
        stats['cout_total_intrants'] = cout_total.quantize(Decimal('0.01'))

    # 3. Données pour les graphiques
    suivis = culture.suivis_pousse.order_by('date_observation')
    stats['graphique_dates'] = [s.date_observation.strftime('%d/%m') for s in suivis]
    stats['graphique_hauteurs'] = [float(s.hauteur_cm) if s.hauteur_cm else None for s in suivis]
    stats['graphique_densites'] = [s.densite_plants if s.densite_plants else None for s in suivis]
    stats['graphique_stades'] = [s.stade_croissance for s in suivis]

    # 4. Résumé observations
    stats['nb_observations'] = suivis.count()
    if suivis.exists():
        derniere = suivis.last()
        stats['derniere_observation'] = derniere.date_observation
        stats['dernier_stade'] = derniere.stade_croissance
        stats['dernier_etat'] = derniere.etat_general

        # Problèmes non résolus (dans les 3 dernières observations)
        problemes = []
        for s in suivis.order_by('-date_observation')[:3]:
            if s.problemes_observes:
                problemes.append(s.problemes_observes)
        stats['problemes_recents'] = problemes

    return stats


def mettre_a_jour_stats(culture):
    """
    Met à jour les stats calculables automatiquement dans StatistiqueCulture.
    Ne touche PAS aux champs manuels déjà remplis (rendement, dates).
    """
    from .models import StatistiqueCulture
    stat, created = StatistiqueCulture.objects.get_or_create(culture=culture)

    auto = calculer_stats_auto(culture)

    # Taux de germination: auto si pas rempli manuellement OU si calculable
    if 'taux_germination' in auto:
        stat.taux_germination = auto['taux_germination']

    # Coût intrants: auto si pas rempli manuellement
    if 'cout_total_intrants' in auto and not stat.cout_total_intrants:
        stat.cout_total_intrants = auto['cout_total_intrants']

    stat.save()
    return stat, auto
