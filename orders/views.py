from datetime import timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Q
from .models import Commande, LigneCommande, Facture
from .forms import CommandeForm, LigneCommandeFormSet, CommandeStatutForm
from accounts.decorators import staff_required, vendeur_or_directeur, directeur_required
from tracking.models import log_action
from .pdf import generer_facture_pdf


def _check_commande_access(user, commande):
    """Vérifie l'accès à une commande."""
    if user.is_directeur() or user.is_superuser:
        return True
    if user.is_vendeur() and commande.vendeur == user:
        return True
    if user.is_magasin():
        return True
    if user.is_client():
        client = getattr(user, 'client_profile', None)
        return client and commande.client == client
    return False


@login_required
def commande_list(request):
    commandes = Commande.objects.select_related('client', 'vendeur').all()

    if request.user.is_client():
        client = getattr(request.user, 'client_profile', None)
        if client:
            commandes = commandes.filter(client=client)
        else:
            commandes = commandes.none()
    elif request.user.is_vendeur():
        commandes = commandes.filter(vendeur=request.user)
    elif request.user.is_magasin():
        commandes = commandes.exclude(statut__in=['livree', 'annulee', 'verification'])

    statut = request.GET.get('statut')
    if statut:
        commandes = commandes.filter(statut=statut)

    return render(request, 'orders/commande_list.html', {
        'commandes': commandes,
        'statuts': Commande.Statut.choices,
        'statut_actif': statut,
    })


@login_required
def commande_detail(request, pk):
    commande = get_object_or_404(Commande, pk=pk)

    if not _check_commande_access(request.user, commande):
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    return render(request, 'orders/commande_detail.html', {'commande': commande})


@vendeur_or_directeur
def commande_create(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        formset = LigneCommandeFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            commande = form.save(commit=False)
            if request.user.is_vendeur():
                commande.vendeur = request.user
            commande.save()
            formset.instance = commande
            formset.save()
            log_action(request.user, 'creation', 'Commande', commande.pk,
                       f'Commande CMD-{commande.pk:05d} créée pour {commande.client.nom_ferme}')
            messages.success(request, f'Commande CMD-{commande.pk:05d} créée.')
            return redirect('orders:commande_detail', pk=commande.pk)
    else:
        form = CommandeForm()
        formset = LigneCommandeFormSet()

        client_pk = request.GET.get('client')
        if client_pk:
            form.fields['client'].initial = client_pk

    return render(request, 'orders/commande_create.html', {
        'form': form, 'formset': formset, 'title': 'Nouvelle commande',
    })


@staff_required
def commande_update_statut(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        if nouveau_statut and commande.peut_transitionner(nouveau_statut):
            ancien_statut = commande.statut
            commande.statut = nouveau_statut
            if nouveau_statut == 'en_preparation' and not commande.preparateur:
                commande.preparateur = request.user
            commande.save()

            # Auto-actions à la livraison
            if nouveau_statut == 'livree':
                _on_livraison(commande)

            log_action(request.user, 'statut', 'Commande', commande.pk,
                       f'CMD-{commande.pk:05d}: {ancien_statut} → {nouveau_statut}')
            messages.success(request, f'Statut mis à jour: {commande.get_statut_display()}')
        elif nouveau_statut:
            messages.error(request, f'Transition {commande.get_statut_display()} → {nouveau_statut} non autorisée.')
    return redirect('orders:commande_detail', pk=commande.pk)


def _on_livraison(commande):
    """Actions automatiques quand une commande passe à 'livrée'."""
    # 1. Déduire le stock
    for ligne in commande.lignes.select_related('produit').all():
        produit = ligne.produit
        qty = int(ligne.quantite)
        ancien_stock = produit.quantite_stock
        produit.quantite_stock = max(0, produit.quantite_stock - qty)
        produit.save(update_fields=['quantite_stock'])
        log_action(None, 'stock', 'Produit', produit.pk,
                   f'Stock {produit.nom}: {ancien_stock} → {produit.quantite_stock} (-{qty}, CMD-{commande.pk:05d})')

    # 2. Auto-créer la facture si elle n'existe pas
    if not Facture.objects.filter(commande=commande).exists():
        echeance = timezone.now().date() + timedelta(days=30)
        facture = Facture.objects.create(
            commande=commande,
            date_echeance=echeance,
        )
        log_action(None, 'creation', 'Facture', facture.pk,
                   f'Facture {facture.numero} auto-créée pour CMD-{commande.pk:05d}')


@vendeur_or_directeur
def commande_valider(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST' and commande.statut == 'verification':
        commande.statut = 'nouvelle'
        commande.save()
        messages.success(request, f'CMD-{commande.pk:05d} validée et envoyée au magasin.')
    return redirect('orders:commande_detail', pk=commande.pk)


@vendeur_or_directeur
def commande_rejeter(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST' and commande.statut == 'verification':
        commande.statut = 'annulee'
        commande.save()
        messages.success(request, f'CMD-{commande.pk:05d} rejetée.')
    return redirect('orders:commande_detail', pk=commande.pk)


@staff_required
def commande_prendre_en_charge(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if commande.statut == 'nouvelle':
        commande.statut = 'en_preparation'
        commande.preparateur = request.user
        commande.save()
        messages.success(request, f'CMD-{commande.pk:05d} prise en charge.')
    return redirect('orders:commande_preparer', pk=commande.pk)


@staff_required
def commande_preparer(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    lignes = commande.lignes.select_related('produit', 'prepare_par').all()

    return render(request, 'orders/commande_preparer.html', {
        'commande': commande,
        'lignes': lignes,
    })


@staff_required
@transaction.atomic
def ligne_toggle_prepare(request, pk):
    ligne = get_object_or_404(LigneCommande.objects.select_for_update(), pk=pk)
    commande = ligne.commande

    if request.method == 'POST':
        if not ligne.prepare:
            ligne.prepare = True
            ligne.prepare_par = request.user
            ligne.date_preparation = timezone.now()
        else:
            ligne.prepare = False
            ligne.prepare_par = None
            ligne.date_preparation = None
        ligne.save()

        if commande.tout_prepare and commande.statut == 'en_preparation':
            commande.statut = 'prete'
            commande.save()
            messages.success(request, f'CMD-{commande.pk:05d} est prête!')
        elif not commande.tout_prepare and commande.statut == 'prete':
            commande.statut = 'en_preparation'
            commande.save()

    return redirect('orders:commande_preparer', pk=commande.pk)


@login_required
def commande_client_create(request):
    client = getattr(request.user, 'client_profile', None)
    if not client:
        messages.error(request, "Aucun profil client associé.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        formset = LigneCommandeFormSet(request.POST)
        if formset.is_valid():
            commande = Commande.objects.create(
                client=client,
                vendeur=client.vendeur,
                notes=request.POST.get('notes', ''),
                statut='verification',
                creee_par_client=True,
            )
            formset.instance = commande
            formset.save()
            messages.success(request, f'Commande CMD-{commande.pk:05d} envoyée pour validation.')
            return redirect('orders:commande_detail', pk=commande.pk)
    else:
        formset = LigneCommandeFormSet()

    return render(request, 'orders/commande_client_form.html', {
        'formset': formset, 'client': client, 'title': 'Passer une commande',
    })


# === FACTURATION ===

@directeur_required
def facture_list(request):
    statut = request.GET.get('statut', '')
    factures = Facture.objects.select_related('commande', 'commande__client').all()
    if statut:
        factures = factures.filter(statut=statut)

    total_impaye = sum(
        (f.total_ttc for f in Facture.objects.filter(statut__in=['envoyee', 'en_retard'])),
        Decimal('0'),
    )
    total_paye_mois = sum(
        (f.total_ttc for f in Facture.objects.filter(
            statut='payee',
            date_paiement__month=timezone.now().month,
            date_paiement__year=timezone.now().year,
        )),
        Decimal('0'),
    )
    nb_en_retard = Facture.objects.filter(statut='en_retard').count()

    return render(request, 'orders/facture_list.html', {
        'factures': factures,
        'statuts': Facture.StatutFacture.choices,
        'statut_actif': statut,
        'total_impaye': total_impaye,
        'total_paye_mois': total_paye_mois,
        'nb_en_retard': nb_en_retard,
    })


@directeur_required
def facture_create(request, commande_pk):
    commande = get_object_or_404(Commande, pk=commande_pk)
    if hasattr(commande, 'facture') and Facture.objects.filter(commande=commande).exists():
        messages.info(request, f'Cette commande a déjà une facture ({commande.facture.numero}).')
        return redirect('orders:facture_detail', pk=commande.facture.pk)
    if commande.statut != 'livree':
        messages.error(request, 'La facture ne peut être créée que pour une commande livrée.')
        return redirect('orders:commande_detail', pk=commande.pk)

    echeance = timezone.now().date() + timedelta(days=30)
    facture = Facture.objects.create(
        commande=commande,
        date_echeance=echeance,
    )
    messages.success(request, f'Facture {facture.numero} créée.')
    return redirect('orders:facture_detail', pk=facture.pk)


@directeur_required
def facture_detail(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    lignes = facture.commande.lignes.select_related('produit').all()
    return render(request, 'orders/facture_detail.html', {
        'facture': facture,
        'lignes': lignes,
    })


@login_required
def facture_pdf(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    return generer_facture_pdf(facture)


@directeur_required
def facture_update_statut(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        new_statut = request.POST.get('statut')
        if new_statut in dict(Facture.StatutFacture.choices):
            facture.statut = new_statut
            if new_statut == 'payee' and not facture.date_paiement:
                facture.date_paiement = timezone.now().date()
            elif new_statut != 'payee':
                facture.date_paiement = None
            facture.save()
            messages.success(request, f'Facture {facture.numero} → {facture.get_statut_display()}')
    return redirect('orders:facture_detail', pk=facture.pk)
