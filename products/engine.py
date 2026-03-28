"""
Moteur de recommandation intelligent pour Herbic CRM.

Analyse le profil complet du client (cultures, historique, suivi de pousse)
et génère des recommandations scorées avec justification.
"""
from datetime import date
from decimal import Decimal
from django.db.models import Q
import math
from .models import RecommandationProduit, Produit, CONVERSIONS


SAISON_PAR_MOIS = {
    1: 'pre_semis', 2: 'pre_semis', 3: 'pre_semis', 4: 'pre_semis',
    5: 'semis',
    6: 'post_levee',
    7: 'croissance',
    8: 'floraison',
    9: 'recolte', 10: 'recolte',
    11: 'pre_semis', 12: 'pre_semis',
}


def get_saison_actuelle():
    return SAISON_PAR_MOIS.get(date.today().month, 'toute_saison')


def calculer_quantite(reco, superficie):
    """
    Calcule le nombre d'unités à commander à partir des champs structurés.

    reco: RecommandationProduit (avec dose_valeur, dose_unite)
    superficie: Decimal (acres)

    Utilise produit.contenance_valeur et produit.contenance_unite
    pour convertir la quantité brute en nombre d'unités (sacs, bidons).
    """
    if not reco.dose_valeur or not superficie:
        return None

    produit = reco.produit
    if not produit.contenance_valeur:
        return None

    try:
        dose = Decimal(str(reco.dose_valeur))
        sup = Decimal(str(superficie))
        total_brut = dose * sup  # ex: 1.67 L/acre * 150 acres = 250.5 L

        # Conversion d'unité si dose_unite != contenance_unite
        dose_u = reco.dose_unite
        cont_u = produit.contenance_unite
        facteur = CONVERSIONS.get((dose_u, cont_u))

        if facteur is None:
            # Mêmes unités ou pas de conversion connue
            if dose_u == cont_u:
                facteur = 1
            else:
                return None  # Unités incompatibles

        total_converti = total_brut * Decimal(str(facteur))
        nb_unites = math.ceil(float(total_converti / Decimal(str(produit.contenance_valeur))))

        return max(1, nb_unites)

    except (ValueError, ArithmeticError, TypeError, ZeroDivisionError):
        return None


def generer_recommandations(client):
    """
    Génère des recommandations intelligentes pour un client.

    Retourne un dict: {culture: [liste de RecoResult]}
    Chaque RecoResult a: produit, score, raisons, quantite_estimee, dose
    """
    cultures = client.cultures.prefetch_related(
        'produits_arrosage', 'suivis_pousse'
    ).all()

    if not cultures:
        return {}

    # Récupérer les produits déjà commandés cette année
    annee = date.today().year
    produits_commandes = set()
    for cmd in client.commandes.filter(date_commande__year=annee):
        for ligne in cmd.lignes.select_related('produit').all():
            produits_commandes.add(ligne.produit.pk)

    # Produits d'arrosage déjà appliqués (par nom)
    produits_appliques_noms = set()
    for culture in cultures:
        for pa in culture.produits_arrosage.all():
            produits_appliques_noms.add(pa.nom_produit.lower().strip())

    saison = get_saison_actuelle()
    resultats = {}

    for culture in cultures:
        recos_brutes = RecommandationProduit.objects.filter(
            type_culture=culture.type_culture_id
        ).select_related('produit', 'produit__categorie', 'complementaire_de')

        if not recos_brutes:
            continue

        # Collecter les problèmes observés dans le suivi
        problemes = set()
        for suivi in culture.suivis_pousse.all():
            if suivi.problemes_observes:
                for mot in suivi.problemes_observes.lower().split():
                    mot = mot.strip('.,;:!()')
                    if len(mot) > 3:
                        problemes.add(mot)

        # Écart population
        ecart_population = None
        if culture.population_visee and culture.population_visee > 0 and culture.population_reelle:
            ecart_population = (
                (culture.population_visee - culture.population_reelle)
                / culture.population_visee
            ) * 100  # en pourcentage

        scored = []

        for reco in recos_brutes:
            produit = reco.produit
            score = reco.priorite
            raisons = []

            # --- CRITÈRE 1: Produit en stock ---
            if not produit.en_stock:
                continue  # ne pas recommander les produits en rupture

            # --- CRITÈRE 2: Déjà acheté cette année ---
            if produit.pk in produits_commandes:
                score -= 15
                raisons.append(('info', 'Déjà commandé cette saison'))

            # --- CRITÈRE 3: Déjà appliqué ---
            nom_lower = produit.nom.lower()
            deja_applique = any(
                nom_lower in pa_nom or pa_nom in nom_lower
                for pa_nom in produits_appliques_noms
            )
            if deja_applique:
                score -= 10
                raisons.append(('info', 'Déjà appliqué sur cette culture'))

            # --- CRITÈRE 4: Saison pertinente ---
            if reco.saison == saison:
                score += 5
                raisons.append(('saison', f'Pertinent maintenant ({reco.get_saison_display()})'))
            elif reco.saison == 'toute_saison':
                pass  # neutre
            else:
                score -= 3

            # --- CRITÈRE 5: Problèmes observés ---
            if reco.probleme_cible and problemes:
                mots_cible = set(
                    m.strip().lower() for m in reco.probleme_cible.split(',')
                )
                match = mots_cible & problemes
                if match:
                    score += 8
                    raisons.append(('alerte', f'Problème détecté: {", ".join(match)}'))

            # --- CRITÈRE 6: Écart population → biostimulants ---
            if ecart_population and ecart_population > 5:
                if produit.categorie.type_categorie == 'biostimulant':
                    score += 6
                    raisons.append(('alerte',
                        f'Population réelle {ecart_population:.0f}% sous la cible'))

            # --- CRITÈRE 7: Complémentarité ---
            if reco.complementaire_de:
                comp_pk = reco.complementaire_de.pk
                if comp_pk in produits_commandes:
                    score += 7
                    raisons.append(('complement',
                        f'Complémentaire de {reco.complementaire_de.nom}'))

            # --- CRITÈRE 8: Superficie → quantité estimée ---
            quantite_estimee = calculer_quantite(reco, culture.superficie_acres)

            # Raison de base (description de la reco)
            if reco.description:
                raisons.insert(0, ('info', reco.description))

            # Ne pas montrer les produits avec un score très négatif
            if score < -5:
                continue

            # Déterminer le label d'unité (sac, bidon, etc.)
            unite_label = ''
            if quantite_estimee and produit.format_produit:
                fmt_lower = produit.format_produit.lower()
                if 'sac' in fmt_lower:
                    unite_label = 'sac' if quantite_estimee == 1 else 'sacs'
                elif 'bidon' in fmt_lower:
                    unite_label = 'bidon' if quantite_estimee == 1 else 'bidons'
                else:
                    unite_label = produit.format_produit.split()[0].lower()

            scored.append({
                'produit': produit,
                'score': score,
                'raisons': raisons,
                'quantite_estimee': quantite_estimee,
                'unite_label': unite_label,
                'dose': reco.dose_affichage or (f'{reco.dose_valeur} {reco.dose_unite}/acre' if reco.dose_valeur else ''),
                'deja_achete': produit.pk in produits_commandes,
                'deja_applique': deja_applique,
                'priorite_originale': reco.priorite,
            })

        # Trier par score décroissant
        scored.sort(key=lambda x: x['score'], reverse=True)
        if scored:
            resultats[culture] = scored

    return resultats
