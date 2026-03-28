"""
Met à jour les recommandations existantes avec les nouveaux champs.
Exécuter avec: python3 update_recos.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'herbic_crm.settings')
django.setup()

from products.models import RecommandationProduit, Produit
from clients.models import TypeCulture

updates = {
    # (code_produit, type_culture): {champs à mettre à jour}
    ('SEM-M001', 'mais'): {
        'dose_par_acre': '80 000 grains/acre (1 sac/2 acres)',
        'saison': 'semis',
    },
    ('SEM-M002', 'mais'): {
        'dose_par_acre': '80 000 grains/acre',
        'saison': 'semis',
    },
    ('HERB-001', 'mais'): {
        'dose_par_acre': '1.67 L/acre',
        'saison': 'post_levee',
        'probleme_cible': 'mauvaises herbes, chiendent',
    },
    ('HERB-003', 'mais'): {
        'dose_par_acre': '315 mL/acre',
        'saison': 'post_levee',
        'probleme_cible': 'graminées, mauvaises herbes',
    },
    ('FONG-002', 'mais'): {
        'dose_par_acre': '500 mL/acre',
        'saison': 'floraison',
        'probleme_cible': 'fusariose, moisissure',
    },
    ('BIO-001', 'mais'): {
        'dose_par_acre': '200 mL/acre',
        'saison': 'semis',
        'probleme_cible': 'faible enracinement, stress',
    },
    ('SEM-S001', 'soya'): {
        'dose_par_acre': '140 000 grains/acre',
        'saison': 'semis',
    },
    ('SEM-S003', 'soya'): {
        'dose_par_acre': '140 000 grains/acre',
        'saison': 'semis',
    },
    ('HERB-001', 'soya'): {
        'dose_par_acre': '1.34 L/acre',
        'saison': 'pre_semis',
        'probleme_cible': 'mauvaises herbes',
    },
    ('HERB-002', 'soya'): {
        'dose_par_acre': '0.59 L/acre',
        'saison': 'post_levee',
        'probleme_cible': 'mauvaises herbes résistantes, kochia',
    },
    ('FONG-003', 'soya'): {
        'dose_par_acre': '800 mL/acre',
        'saison': 'floraison',
        'probleme_cible': 'cercospora, rouille, sclérotinia',
    },
    ('ENG-002', 'soya'): {
        'dose_par_acre': '2 L/acre',
        'saison': 'floraison',
    },
    ('SEM-B001', 'ble'): {
        'dose_par_acre': '120 lb/acre',
        'saison': 'semis',
    },
    ('HERB-004', 'ble'): {
        'dose_par_acre': '0.41 L/acre',
        'saison': 'post_levee',
        'probleme_cible': 'mauvaises herbes, chardon',
    },
    ('FONG-001', 'ble'): {
        'dose_par_acre': '0.8 L/acre',
        'saison': 'floraison',
        'probleme_cible': 'fusariose, septoriose',
    },
    ('ENG-003', 'ble'): {
        'dose_par_acre': '1 L/acre',
        'saison': 'croissance',
        'probleme_cible': 'carence manganèse, jaunissement',
    },
}

# Complémentarités: si le client achète X, recommander Y
complementaires = {
    ('HERB-003', 'mais'): 'HERB-001',  # Callisto complémentaire au Roundup
    ('FONG-002', 'mais'): 'SEM-M001',  # Fongicide si semence Pioneer
    ('HERB-002', 'soya'): 'HERB-001',  # Engenia complémentaire au Roundup
    ('FONG-003', 'soya'): 'SEM-S001',  # Fongicide si semence Prograin
    ('FONG-001', 'ble'): 'SEM-B001',   # Fongicide si blé Bolles
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
