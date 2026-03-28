from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Client, Culture, ProduitArrosage, TypeCulture
from .forms import ClientForm, CultureForm, ProduitArrosageForm, ClientSearchForm, TypeCultureForm
from accounts.decorators import staff_required, vendeur_or_directeur, directeur_required
from products.engine import generer_recommandations


def _check_client_access(user, client):
    """Vérifie qu'un vendeur a accès à ce client. Directeur a toujours accès."""
    if user.is_directeur() or user.is_superuser:
        return True
    if user.is_vendeur() and client.vendeur == user:
        return True
    if user.is_client() and client.user == user:
        return True
    return False


@login_required
def client_list(request):
    form = ClientSearchForm(request.GET)
    clients = Client.objects.select_related('vendeur').all()

    if request.user.is_vendeur():
        clients = clients.filter(vendeur=request.user)
    elif request.user.is_client():
        clients = clients.filter(user=request.user)

    q = request.GET.get('q', '')
    if q:
        clients = clients.filter(
            Q(nom__icontains=q) |
            Q(prenom__icontains=q) |
            Q(nom_ferme__icontains=q) |
            Q(code__icontains=q) |
            Q(ville__icontains=q)
        )

    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'search_form': form,
    })


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if not _check_client_access(request.user, client):
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    cultures = client.cultures.select_related('type_culture').prefetch_related(
        'produits_arrosage', 'suivis_pousse'
    ).all()
    commandes = client.commandes.select_related('vendeur').all()[:10]

    recommandations = generer_recommandations(client)

    return render(request, 'clients/client_detail.html', {
        'client': client,
        'cultures': cultures,
        'commandes': commandes,
        'recommandations': recommandations,
    })


@vendeur_or_directeur
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            if request.user.is_vendeur():
                client.vendeur = request.user
            client.save()
            messages.success(request, f'Client "{client.nom_ferme}" créé.')
            return redirect('clients:client_detail', pk=client.pk)
    else:
        form = ClientForm()
        if request.user.is_vendeur():
            form.fields['vendeur'].initial = request.user.pk
            form.fields['vendeur'].widget.attrs['disabled'] = True
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Nouveau client'})


@vendeur_or_directeur
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if not _check_client_access(request.user, client):
        messages.error(request, "Vous ne pouvez pas modifier ce client.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            c = form.save(commit=False)
            if request.user.is_vendeur():
                c.vendeur = request.user
            c.save()
            messages.success(request, 'Client mis à jour.')
            return redirect('clients:client_detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
        if request.user.is_vendeur():
            form.fields['vendeur'].widget.attrs['disabled'] = True
    return render(request, 'clients/client_form.html', {'form': form, 'title': f'Modifier {client.nom_ferme}'})


@vendeur_or_directeur
def culture_create(request, client_pk):
    client = get_object_or_404(Client, pk=client_pk)
    if not _check_client_access(request.user, client):
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CultureForm(request.POST)
        if form.is_valid():
            culture = form.save(commit=False)
            culture.client = client
            culture.save()
            messages.success(request, 'Culture ajoutée.')
            return redirect('clients:client_detail', pk=client.pk)
    else:
        form = CultureForm()
    return render(request, 'clients/culture_form.html', {
        'form': form, 'client': client, 'title': 'Ajouter une culture',
    })


@vendeur_or_directeur
def culture_edit(request, pk):
    culture = get_object_or_404(Culture, pk=pk)
    if not _check_client_access(request.user, culture.client):
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CultureForm(request.POST, instance=culture)
        if form.is_valid():
            form.save()
            messages.success(request, 'Culture mise à jour.')
            return redirect('clients:client_detail', pk=culture.client.pk)
    else:
        form = CultureForm(instance=culture)
    return render(request, 'clients/culture_form.html', {
        'form': form, 'client': culture.client, 'title': 'Modifier la culture',
    })


@vendeur_or_directeur
def produit_arrosage_create(request, culture_pk):
    culture = get_object_or_404(Culture, pk=culture_pk)
    if not _check_client_access(request.user, culture.client):
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = ProduitArrosageForm(request.POST)
        if form.is_valid():
            pa = form.save(commit=False)
            pa.culture = culture
            pa.save()
            messages.success(request, "Produit d'arrosage ajouté.")
            return redirect('clients:client_detail', pk=culture.client.pk)
    else:
        form = ProduitArrosageForm()
    return render(request, 'clients/produit_arrosage_form.html', {
        'form': form, 'culture': culture, 'title': "Ajouter un produit d'arrosage",
    })


# === TYPES DE CULTURE (directeur) ===

@directeur_required
def type_culture_list(request):
    types = TypeCulture.objects.annotate(nb_cultures=Count('cultures')).all()
    return render(request, 'clients/type_culture_list.html', {'types': types})


@directeur_required
def type_culture_create(request):
    if request.method == 'POST':
        form = TypeCultureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type de culture créé.')
            return redirect('clients:type_culture_list')
    else:
        form = TypeCultureForm()
    return render(request, 'clients/type_culture_form.html', {'form': form, 'title': 'Nouveau type de culture'})


@directeur_required
def type_culture_edit(request, pk):
    tc = get_object_or_404(TypeCulture, pk=pk)
    if request.method == 'POST':
        form = TypeCultureForm(request.POST, instance=tc)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type de culture mis à jour.')
            return redirect('clients:type_culture_list')
    else:
        form = TypeCultureForm(instance=tc)
    return render(request, 'clients/type_culture_form.html', {'form': form, 'title': f'Modifier {tc.nom}'})


@directeur_required
def type_culture_delete(request, pk):
    tc = get_object_or_404(TypeCulture, pk=pk)
    if request.method == 'POST':
        if tc.cultures.exists():
            messages.error(request, 'Impossible: des cultures utilisent ce type.')
        else:
            nom = tc.nom
            tc.delete()
            messages.success(request, f'Type "{nom}" supprimé.')
    return redirect('clients:type_culture_list')
