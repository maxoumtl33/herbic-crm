from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Client, Culture, ProduitArrosage
from .forms import ClientForm, CultureForm, ProduitArrosageForm, ClientSearchForm
from accounts.decorators import staff_required, vendeur_or_directeur
from products.models import RecommandationProduit


@login_required
def client_list(request):
    form = ClientSearchForm(request.GET)
    clients = Client.objects.all()

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

    if request.user.is_client() and client.user != request.user:
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    cultures = client.cultures.all()
    commandes = client.commandes.all()[:10]

    recommandations = {}
    for culture in cultures:
        recos = RecommandationProduit.objects.filter(
            type_culture=culture.type_culture
        ).select_related('produit')
        if recos.exists():
            recommandations[culture] = recos

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
            if request.user.is_vendeur() and not client.vendeur:
                client.vendeur = request.user
            client.save()
            messages.success(request, f'Client "{client.nom_ferme}" créé.')
            return redirect('clients:client_detail', pk=client.pk)
    else:
        form = ClientForm()
        if request.user.is_vendeur():
            form.fields['vendeur'].initial = request.user.pk
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Nouveau client'})


@vendeur_or_directeur
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client mis à jour.')
            return redirect('clients:client_detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/client_form.html', {'form': form, 'title': f'Modifier {client.nom_ferme}'})


@vendeur_or_directeur
def culture_create(request, client_pk):
    client = get_object_or_404(Client, pk=client_pk)
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
