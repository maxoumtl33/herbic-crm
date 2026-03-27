from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Décorateur qui restreint l'accès aux rôles spécifiés."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request, "Vous n'avez pas accès à cette page.")
                return redirect('accounts:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def staff_required(view_func):
    """Accès pour vendeurs, magasin et directeurs."""
    return role_required('vendeur', 'magasin', 'directeur')(view_func)


def vendeur_or_directeur(view_func):
    """Accès pour vendeurs et directeurs."""
    return role_required('vendeur', 'directeur')(view_func)


def directeur_required(view_func):
    """Accès pour directeurs uniquement."""
    return role_required('directeur')(view_func)
