from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('accounts:dashboard')),
    path('comptes/', include('accounts.urls')),
    path('clients/', include('clients.urls')),
    path('produits/', include('products.urls')),
    path('commandes/', include('orders.urls')),
    path('suivi/', include('tracking.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
