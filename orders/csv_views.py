"""Import/export CSV."""
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.decorators import directeur_required
from products.models import Produit
from clients.models import Client
from orders.models import Commande


@directeur_required
def export_produits_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="produits_herbic.csv"'
    response.write('\ufeff')  # BOM UTF-8 pour Excel

    writer = csv.writer(response)
    writer.writerow(['Code', 'Nom', 'Catégorie', 'Format', 'Prix unitaire', 'Stock', 'Seuil alerte', 'En stock'])

    for p in Produit.objects.select_related('categorie').all():
        writer.writerow([
            p.code, p.nom, str(p.categorie), p.format_produit,
            p.prix_unitaire or '', p.quantite_stock, p.seuil_alerte_stock,
            'Oui' if p.en_stock else 'Non',
        ])
    return response


@directeur_required
def export_clients_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clients_herbic.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Code', 'Ferme', 'Prénom', 'Nom', 'Adresse', 'Ville', 'Code postal',
                     'Téléphone', 'Cellulaire', 'Courriel', 'Vendeur'])

    for c in Client.objects.select_related('vendeur').all():
        writer.writerow([
            c.code, c.nom_ferme, c.prenom, c.nom, c.adresse, c.ville, c.code_postal,
            c.telephone, c.cellulaire, c.courriel,
            c.vendeur.get_full_name() if c.vendeur else '',
        ])
    return response


@directeur_required
def export_commandes_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="commandes_herbic.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['No', 'Client', 'Vendeur', 'Statut', 'Date', 'Total HT', 'Nb produits'])

    for cmd in Commande.objects.select_related('client', 'vendeur').all():
        writer.writerow([
            f'CMD-{cmd.pk:05d}', cmd.client.nom_ferme,
            cmd.vendeur.get_full_name() if cmd.vendeur else '',
            cmd.get_statut_display(), cmd.date_commande.strftime('%Y-%m-%d'),
            cmd.total, cmd.nb_lignes,
        ])
    return response


@directeur_required
def export_stocks_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stocks_herbic.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Code', 'Produit', 'Catégorie', 'Stock actuel', 'Seuil alerte', 'Contenant', 'Prix unitaire'])

    for p in Produit.objects.select_related('categorie').all():
        writer.writerow([
            p.code, p.nom, str(p.categorie), p.quantite_stock,
            p.seuil_alerte_stock, p.get_contenant_display(), p.prix_unitaire or '',
        ])
    return response
