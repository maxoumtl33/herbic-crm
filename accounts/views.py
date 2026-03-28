from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UserCreateForm, UserEditForm, UserUpdateForm
from .decorators import directeur_required
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('accounts:dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.is_client():
        client = getattr(user, 'client_profile', None)
        if client:
            context['client'] = client
            context['commandes'] = client.commandes.all()[:10]
            context['cultures'] = client.cultures.all()
        return render(request, 'accounts/dashboard_client.html', context)

    elif user.is_vendeur():
        from orders.models import Commande
        context['clients'] = user.clients_assignes.all()
        context['commandes_recentes'] = user.commandes_vendeur.order_by('-date_commande')[:10]
        context['commandes_en_livraison'] = user.commandes_vendeur.filter(
            statut='en_livraison'
        ).select_related('client').order_by('date_commande')
        context['commandes_pretes'] = user.commandes_vendeur.filter(
            statut='prete'
        ).select_related('client').order_by('date_commande')
        context['commandes_verification'] = user.commandes_vendeur.filter(
            statut='verification'
        ).select_related('client').order_by('date_commande')
        return render(request, 'accounts/dashboard_vendeur.html', context)

    elif user.is_magasin():
        from orders.models import Commande
        context['commandes_nouvelles'] = Commande.objects.filter(
            statut='nouvelle'
        ).select_related('client', 'vendeur').order_by('date_commande')
        context['commandes_en_preparation'] = Commande.objects.filter(
            statut='en_preparation'
        ).select_related('client', 'preparateur').order_by('date_commande')
        context['commandes_pretes'] = Commande.objects.filter(
            statut='prete'
        ).select_related('client').order_by('date_commande')
        context['commandes_en_livraison'] = Commande.objects.filter(
            statut='en_livraison'
        ).select_related('client').order_by('date_commande')
        context['total_aujourdhui'] = Commande.objects.exclude(
            statut__in=['livree', 'annulee']
        ).count()
        return render(request, 'accounts/dashboard_magasin.html', context)

    else:  # directeur
        from orders.models import Commande, Facture
        from clients.models import Client
        from django.utils import timezone
        context['total_clients'] = Client.objects.count()
        context['commandes_en_cours'] = Commande.objects.exclude(
            statut__in=['livree', 'annulee']
        ).count()
        context['commandes_recentes'] = Commande.objects.order_by('-date_commande')[:10]
        context['commandes_verification'] = Commande.objects.filter(
            statut='verification'
        ).select_related('client', 'vendeur').order_by('date_commande')
        context['vendeurs'] = User.objects.filter(role='vendeur')
        # Facturation
        context['factures_impayees'] = Facture.objects.filter(
            statut__in=['envoyee', 'en_retard']
        ).select_related('commande', 'commande__client').order_by('date_echeance')[:5]
        context['total_impaye'] = sum(
            f.total_ttc for f in Facture.objects.filter(statut__in=['envoyee', 'en_retard'])
        )
        context['nb_factures_retard'] = Facture.objects.filter(statut='en_retard').count()
        context['commandes_sans_facture'] = Commande.objects.filter(
            statut='livree'
        ).exclude(facture__isnull=False).select_related('client')[:5]
        return render(request, 'accounts/dashboard_directeur.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour.')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@directeur_required
def user_list(request):
    role_filter = request.GET.get('role', '')
    users = User.objects.all().order_by('role', 'last_name')
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'accounts/user_list.html', {
        'users': users,
        'role_filter': role_filter,
        'roles': User.Role.choices,
    })


@directeur_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur créé.')
            return redirect('accounts:user_list')
    else:
        form = UserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Nouvel utilisateur'})


@directeur_required
def user_edit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Utilisateur "{user_obj.username}" mis à jour.')
            return redirect('accounts:user_list')
    else:
        form = UserEditForm(instance=user_obj)
    return render(request, 'accounts/user_form.html', {'form': form, 'title': f'Modifier {user_obj.get_full_name() or user_obj.username}'})


@directeur_required
def user_toggle_active(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user_obj == request.user:
            messages.error(request, 'Vous ne pouvez pas vous désactiver vous-même.')
        else:
            user_obj.is_active = not user_obj.is_active
            user_obj.save()
            etat = 'activé' if user_obj.is_active else 'désactivé'
            messages.success(request, f'{user_obj.get_full_name() or user_obj.username} {etat}.')
    return redirect('accounts:user_list')


@directeur_required
def journal_activite(request):
    from tracking.models import JournalActivite
    entries = JournalActivite.objects.select_related('utilisateur').all()[:100]
    return render(request, 'accounts/journal.html', {'entries': entries})
