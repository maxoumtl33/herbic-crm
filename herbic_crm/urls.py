from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from orders.api_views import api_produits, api_clients, api_recherche_globale
from orders.csv_views import export_produits_csv, export_clients_csv, export_commandes_csv, export_stocks_csv

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('accounts:dashboard')),
    path('comptes/', include('accounts.urls')),
    path('clients/', include('clients.urls')),
    path('produits/', include('products.urls')),
    path('commandes/', include('orders.urls')),
    path('suivi/', include('tracking.urls')),
    # API JSON
    path('api/produits/', api_produits, name='api_produits'),
    path('api/clients/', api_clients, name='api_clients'),
    path('api/recherche/', api_recherche_globale, name='api_recherche'),
    # Exports CSV
    path('export/produits/', export_produits_csv, name='export_produits'),
    path('export/clients/', export_clients_csv, name='export_clients'),
    path('export/commandes/', export_commandes_csv, name='export_commandes'),
    path('export/stocks/', export_stocks_csv, name='export_stocks'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
