"""
Moteur de calcul automatique des statistiques de culture.
"""
import math
from decimal import Decimal, ROUND_HALF_UP
from products.models import Produit, CONVERSIONS


def calculer_cout_produit(pa):
    """
    Calcule le coût d'un produit d'arrosage appliqué.

    Logique:
    - pa.quantite_totale = quantité brute appliquée (ex: 250.5 L, 47.25 L)
    - pa.unite = unité (L, mL, kg...)
    - On cherche le produit au catalogue par nom
    - On convertit en nombre d'unités (bidons, sacs) achetées
    - Coût = nb_unités × prix_unitaire

    Retourne (cout, detail_dict) ou (None, None)
    """
    # Chercher le produit au catalogue
    nom_mots = pa.nom_produit.strip().split()
    produit = None
    for i in range(len(nom_mots), 0, -1):
        recherche = ' '.join(nom_mots[:i])
        results = Produit.objects.filter(nom__icontains=recherche)
        if results.count() == 1:
            produit = results.first()
            break

    if not produit or not produit.prix_unitaire or not pa.quantite_totale:
        return None, None

    if not produit.contenance_valeur:
        return None, None

    # Convertir la quantité dans l'unité du produit
    pa_unite = pa.unite.strip()
    prod_unite = produit.contenance_unite

    facteur = CONVERSIONS.get((pa_unite, prod_unite))
    if facteur is None:
        if pa_unite.lower() == prod_unite.lower():
            facteur = 1
        else:
            return None, None

    quantite_convertie = Decimal(str(pa.quantite_totale)) * Decimal(str(facteur))
    nb_unites = math.ceil(float(quantite_convertie / produit.contenance_valeur))
    cout = Decimal(str(nb_unites)) * produit.prix_unitaire

    return cout, {
        'nom': pa.nom_produit,
        'produit_catalogue': produit.nom,
        'quantite_appliquee': f'{pa.quantite_totale} {pa.unite}',
        'nb_unites': nb_unites,
        'contenant': produit.get_contenant_display(),
        'prix_unitaire': produit.prix_unitaire,
        'cout': cout.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
    }


def calculer_stats_auto(culture):
    """
    Calcule les statistiques automatiques pour une culture.
    """
    stats = {}

    # 1. Taux de germination
    if culture.population_visee and culture.population_reelle:
        stats['taux_germination'] = round(
            (culture.population_reelle / culture.population_visee) * 100, 1
        )

    # 2. Coût produits - détaillé
    cout_total = Decimal('0')
    detail_couts = []
    for pa in culture.produits_arrosage.all():
        cout, detail = calculer_cout_produit(pa)
        if cout and detail:
            cout_total += cout
            detail_couts.append(detail)

    if detail_couts:
        stats['cout_total_intrants'] = cout_total.quantize(Decimal('0.01'))
        stats['detail_couts'] = detail_couts
        if culture.superficie_acres:
            cout_acre = (cout_total / Decimal(str(culture.superficie_acres))).quantize(Decimal('0.01'))
            stats['cout_par_acre'] = cout_acre

    # 3. Données pour les graphiques
    suivis = culture.suivis_pousse.order_by('date_observation')
    stats['graphique_dates'] = [s.date_observation.strftime('%d/%m') for s in suivis]
    stats['graphique_hauteurs'] = [float(s.hauteur_cm) if s.hauteur_cm else None for s in suivis]
    stats['graphique_densites'] = [s.densite_plants if s.densite_plants else None for s in suivis]
    stats['graphique_stades'] = [s.stade_croissance for s in suivis]
    stats['graphique_etats'] = [s.etat_general for s in suivis]

    # 4. Résumé observations
    stats['nb_observations'] = suivis.count()
    if suivis.exists():
        derniere = suivis.last()
        stats['derniere_observation'] = derniere.date_observation
        stats['dernier_stade'] = derniere.stade_croissance
        stats['dernier_etat'] = derniere.etat_general

        problemes = []
        for s in suivis.order_by('-date_observation')[:3]:
            if s.problemes_observes:
                problemes.append(s.problemes_observes)
        stats['problemes_recents'] = problemes

    return stats


def mettre_a_jour_stats(culture):
    from .models import StatistiqueCulture
    stat, created = StatistiqueCulture.objects.get_or_create(culture=culture)

    auto = calculer_stats_auto(culture)

    if 'taux_germination' in auto:
        stat.taux_germination = auto['taux_germination']

    if 'cout_total_intrants' in auto:
        stat.cout_total_intrants = auto['cout_total_intrants']

    stat.save()
    return stat, auto
