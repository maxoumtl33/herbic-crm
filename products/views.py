from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Produit, CategorieProduit, RecommandationProduit
from .forms import ProduitForm, CategorieForm, RecommandationForm
from accounts.decorators import staff_required, directeur_required
from clients.models import Culture


@login_required
def produit_list(request):
    produits = Produit.objects.select_related('categorie').all()
    categorie = request.GET.get('categorie')
    q = request.GET.get('q', '')

    if categorie:
        produits = produits.filter(categorie__type_categorie=categorie)
    if q:
        produits = produits.filter(
            Q(nom__icontains=q) | Q(code__icontains=q) | Q(description__icontains=q)
        )

    categories = CategorieProduit.TypeCategorie.choices
    return render(request, 'products/produit_list.html', {
        'produits': produits,
        'categories': categories,
        'categorie_active': categorie,
        'q': q,
    })


@login_required
def produit_detail(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    recommandations = produit.recommandations.all()
    return render(request, 'products/produit_detail.html', {
        'produit': produit,
        'recommandations': recommandations,
    })


@directeur_required
def produit_create(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit créé.')
            return redirect('products:produit_list')
    else:
        form = ProduitForm()
    return render(request, 'products/produit_form.html', {'form': form, 'title': 'Nouveau produit'})


@directeur_required
def produit_edit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit mis à jour.')
            return redirect('products:produit_detail', pk=produit.pk)
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'products/produit_form.html', {'form': form, 'title': f'Modifier {produit.nom}'})


@directeur_required
def produit_delete(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        nom = produit.nom
        produit.delete()
        messages.success(request, f'Produit "{nom}" supprimé.')
        return redirect('products:produit_list')
    return render(request, 'products/produit_confirm_delete.html', {'produit': produit})


# === CATÉGORIES ===

@directeur_required
def categorie_list(request):
    categories = CategorieProduit.objects.annotate(
        nb_produits=Count('produits')
    ).order_by('type_categorie', 'nom')
    return render(request, 'products/categorie_list.html', {'categories': categories})


@directeur_required
def categorie_create(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie créée.')
            return redirect('products:categorie_list')
    else:
        form = CategorieForm()
    return render(request, 'products/categorie_form.html', {'form': form, 'title': 'Nouvelle catégorie'})


@directeur_required
def categorie_edit(request, pk):
    categorie = get_object_or_404(CategorieProduit, pk=pk)
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie mise à jour.')
            return redirect('products:categorie_list')
    else:
        form = CategorieForm(instance=categorie)
    return render(request, 'products/categorie_form.html', {'form': form, 'title': f'Modifier {categorie.nom}'})


@directeur_required
def categorie_delete(request, pk):
    categorie = get_object_or_404(CategorieProduit, pk=pk)
    if request.method == 'POST':
        if categorie.produits.exists():
            messages.error(request, 'Impossible de supprimer: des produits utilisent cette catégorie.')
        else:
            nom = categorie.nom
            categorie.delete()
            messages.success(request, f'Catégorie "{nom}" supprimée.')
        return redirect('products:categorie_list')
    return redirect('products:categorie_list')


# === RECOMMANDATIONS ===

@directeur_required
def recommandation_list(request):
    type_culture = request.GET.get('culture', '')
    recommandations = RecommandationProduit.objects.select_related('produit', 'produit__categorie').all()

    if type_culture:
        recommandations = recommandations.filter(type_culture=type_culture)

    types_culture = Culture.TypeCulture.choices
    return render(request, 'products/recommandation_list.html', {
        'recommandations': recommandations,
        'types_culture': types_culture,
        'culture_active': type_culture,
    })


@directeur_required
def recommandation_create(request):
    if request.method == 'POST':
        form = RecommandationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recommandation ajoutée.')
            return redirect('products:recommandation_list')
    else:
        form = RecommandationForm()
        # Pré-remplir avec les choix de culture
        form.fields['type_culture'].widget = __import__('django.forms', fromlist=['Select']).Select(
            attrs={'class': 'form-control'},
            choices=[('', '---')] + list(Culture.TypeCulture.choices),
        )
    return render(request, 'products/recommandation_form.html', {'form': form, 'title': 'Nouvelle recommandation'})


@directeur_required
def recommandation_edit(request, pk):
    reco = get_object_or_404(RecommandationProduit, pk=pk)
    if request.method == 'POST':
        form = RecommandationForm(request.POST, instance=reco)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recommandation mise à jour.')
            return redirect('products:recommandation_list')
    else:
        form = RecommandationForm(instance=reco)
        form.fields['type_culture'].widget = __import__('django.forms', fromlist=['Select']).Select(
            attrs={'class': 'form-control'},
            choices=[('', '---')] + list(Culture.TypeCulture.choices),
        )
    return render(request, 'products/recommandation_form.html', {'form': form, 'title': 'Modifier la recommandation'})


@directeur_required
def recommandation_delete(request, pk):
    reco = get_object_or_404(RecommandationProduit, pk=pk)
    if request.method == 'POST':
        reco.delete()
        messages.success(request, 'Recommandation supprimée.')
    return redirect('products:recommandation_list')
