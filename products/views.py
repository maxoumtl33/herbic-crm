from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Produit, CategorieProduit
from .forms import ProduitForm, CategorieForm
from accounts.decorators import staff_required, directeur_required


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
    return render(request, 'products/produit_detail.html', {'produit': produit})


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
