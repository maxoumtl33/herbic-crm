"""
Met à jour les recommandations existantes avec doses structurées.
Exécuter avec: python3 update_recos.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'herbic_crm.settings')
django.setup()

from products.models import RecommandationProduit, Produit
from clients.models import TypeCulture

# (code_produit, type_culture): {dose_valeur, dose_unite, dose_affichage, saison, probleme_cible}
updates = {
    ('SEM-M001', 'mais'): {
        'dose_valeur': 80000, 'dose_unite': 'grains',
        'dose_affichage': '80 000 grains/acre (1 sac/2 acres)',
        'saison': 'semis',
    },
    ('SEM-M002', 'mais'): {
        'dose_valeur': 80000, 'dose_unite': 'grains',
        'dose_affichage': '80 000 grains/acre',
        'saison': 'semis',
    },
    ('HERB-001', 'mais'): {
        'dose_valeur': 1.67, 'dose_unite': 'L',
        'dose_affichage': '1.67 L/acre',
        'saison': 'post_levee',
        'probleme_cible': 'mauvaises herbes, chiendent',
    },
    ('HERB-003', 'mais'): {
        'dose_valeur': 315, 'dose_unite': 'mL',
        'dose_affichage': '315 mL/acre',
        'saison': 'post_levee',
        'probleme_cible': 'graminées, mauvaises herbes',
    },
    ('FONG-002', 'mais'): {
        'dose_valeur': 500, 'dose_unite': 'mL',
        'dose_affichage': '500 mL/acre',
        'saison': 'floraison',
        'probleme_cible': 'fusariose, moisissure',
    },
    ('BIO-001', 'mais'): {
        'dose_valeur': 200, 'dose_unite': 'mL',
        'dose_affichage': '200 mL/acre',
        'saison': 'semis',
        'probleme_cible': 'faible enracinement, stress',
    },
    ('SEM-S001', 'soya'): {
        'dose_valeur': 140000, 'dose_unite': 'grains',
        'dose_affichage': '140 000 grains/acre',
        'saison': 'semis',
    },
    ('SEM-S003', 'soya'): {
        'dose_valeur': 140000, 'dose_unite': 'grains',
        'dose_affichage': '140 000 grains/acre',
        'saison': 'semis',
    },
    ('HERB-001', 'soya'): {
        'dose_valeur': 1.34, 'dose_unite': 'L',
        'dose_affichage': '1.34 L/acre',
        'saison': 'pre_semis',
        'probleme_cible': 'mauvaises herbes',
    },
    ('HERB-002', 'soya'): {
        'dose_valeur': 0.59, 'dose_unite': 'L',
        'dose_affichage': '0.59 L/acre',
        'saison': 'post_levee',
        'probleme_cible': 'mauvaises herbes résistantes, kochia',
    },
    ('FONG-003', 'soya'): {
        'dose_valeur': 800, 'dose_unite': 'mL',
        'dose_affichage': '800 mL/acre',
        'saison': 'floraison',
        'probleme_cible': 'cercospora, rouille, sclérotinia',
    },
    ('ENG-002', 'soya'): {
        'dose_valeur': 2, 'dose_unite': 'L',
        'dose_affichage': '2 L/acre',
        'saison': 'floraison',
    },
    ('SEM-B001', 'ble'): {
        'dose_valeur': 120, 'dose_unite': 'lb',
        'dose_affichage': '120 lb/acre',
        'saison': 'semis',
    },
    ('HERB-004', 'ble'): {
        'dose_valeur': 0.41, 'dose_unite': 'L',
        'dose_affichage': '0.41 L/acre',
        'saison': 'post_levee',
        'probleme_cible': 'mauvaises herbes, chardon',
    },
    ('FONG-001', 'ble'): {
        'dose_valeur': 0.8, 'dose_unite': 'L',
        'dose_affichage': '0.8 L/acre',
        'saison': 'floraison',
        'probleme_cible': 'fusariose, septoriose',
    },
    ('ENG-003', 'ble'): {
        'dose_valeur': 1, 'dose_unite': 'L',
        'dose_affichage': '1 L/acre',
        'saison': 'croissance',
        'probleme_cible': 'carence manganèse, jaunissement',
    },
}

complementaires = {
    ('HERB-003', 'mais'): 'HERB-001',
    ('FONG-002', 'mais'): 'SEM-M001',
    ('HERB-002', 'soya'): 'HERB-001',
    ('FONG-003', 'soya'): 'SEM-S001',
    ('FONG-001', 'ble'): 'SEM-B001',
}

updated = 0
for (code, culture), data in updates.items():
    try:
        produit = Produit.objects.get(code=code)
        reco = RecommandationProduit.objects.get(produit=produit, type_culture__code=culture)
        for key, val in data.items():
            setattr(reco, key, val)
        reco.save()
        updated += 1
        print(f"  Mis à jour: {produit.nom} -> {culture}")
    except (Produit.DoesNotExist, RecommandationProduit.DoesNotExist):
        print(f"  Pas trouvé: {code} -> {culture}")

for (code, culture), comp_code in complementaires.items():
    try:
        produit = Produit.objects.get(code=code)
        comp = Produit.objects.get(code=comp_code)
        reco = RecommandationProduit.objects.get(produit=produit, type_culture__code=culture)
        reco.complementaire_de = comp
        reco.save()
        print(f"  Complémentaire: {produit.nom} <-> {comp.nom}")
    except (Produit.DoesNotExist, RecommandationProduit.DoesNotExist):
        pass

print(f"\n{updated} recommandations mises à jour.")
