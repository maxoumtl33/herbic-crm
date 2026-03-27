from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Commande, LigneCommande
from .forms import CommandeForm, LigneCommandeFormSet, CommandeStatutForm
from accounts.decorators import staff_required, vendeur_or_directeur


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
        commandes = commandes.exclude(statut__in=['livree', 'annulee'])

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

    if request.user.is_client():
        client = getattr(request.user, 'client_profile', None)
        if not client or commande.client != client:
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
            messages.success(request, f'Commande CMD-{commande.pk:05d} créée.')
            return redirect('orders:commande_detail', pk=commande.pk)
    else:
        form = CommandeForm()
        formset = LigneCommandeFormSet()

        client_pk = request.GET.get('client')
        if client_pk:
            form.fields['client'].initial = client_pk

    return render(request, 'orders/commande_form.html', {
        'form': form, 'formset': formset, 'title': 'Nouvelle commande',
    })


@staff_required
def commande_update_statut(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        form = CommandeStatutForm(request.POST, instance=commande)
        if form.is_valid():
            cmd = form.save(commit=False)
            if cmd.statut == 'en_preparation' and not cmd.preparateur:
                cmd.preparateur = request.user
            cmd.save()
            messages.success(request, f'Statut mis à jour: {cmd.get_statut_display()}')
    return redirect('orders:commande_detail', pk=commande.pk)


@staff_required
def commande_prendre_en_charge(request, pk):
    """Le magasin prend en charge une commande nouvelle -> en préparation."""
    commande = get_object_or_404(Commande, pk=pk)
    if commande.statut == 'nouvelle':
        commande.statut = 'en_preparation'
        commande.preparateur = request.user
        commande.save()
        messages.success(request, f'CMD-{commande.pk:05d} prise en charge.')
    return redirect('orders:commande_preparer', pk=commande.pk)


@staff_required
def commande_preparer(request, pk):
    """Vue de préparation: cocher les produits un par un."""
    commande = get_object_or_404(Commande, pk=pk)
    lignes = commande.lignes.select_related('produit', 'prepare_par').all()

    return render(request, 'orders/commande_preparer.html', {
        'commande': commande,
        'lignes': lignes,
    })


@staff_required
def ligne_toggle_prepare(request, pk):
    """Toggle l'état préparé d'une ligne de commande."""
    ligne = get_object_or_404(LigneCommande, pk=pk)
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

        # Auto-transition: si tout est préparé -> prête
        if commande.tout_prepare and commande.statut == 'en_preparation':
            commande.statut = 'prete'
            commande.save()
            messages.success(request, f'CMD-{commande.pk:05d} est prête!')
        # Si on décoche et la commande était prête -> retour en préparation
        elif not commande.tout_prepare and commande.statut == 'prete':
            commande.statut = 'en_preparation'
            commande.save()

    return redirect('orders:commande_preparer', pk=commande.pk)


@login_required
def commande_client_create(request):
    """Permet au client de passer une commande lui-même."""
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
            )
            formset.instance = commande
            formset.save()
            messages.success(request, f'Commande CMD-{commande.pk:05d} envoyée.')
            return redirect('orders:commande_detail', pk=commande.pk)
    else:
        formset = LigneCommandeFormSet()

    return render(request, 'orders/commande_client_form.html', {
        'formset': formset, 'client': client, 'title': 'Passer une commande',
    })
