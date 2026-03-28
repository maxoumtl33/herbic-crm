from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.commande_list, name='commande_list'),
    path('<int:pk>/', views.commande_detail, name='commande_detail'),
    path('creer/', views.commande_create, name='commande_create'),
    path('<int:pk>/statut/', views.commande_update_statut, name='commande_update_statut'),
    path('<int:pk>/prendre/', views.commande_prendre_en_charge, name='commande_prendre'),
    path('<int:pk>/preparer/', views.commande_preparer, name='commande_preparer'),
    path('ligne/<int:pk>/toggle/', views.ligne_toggle_prepare, name='ligne_toggle_prepare'),
    path('ma-commande/', views.commande_client_create, name='commande_client_create'),
    # Facturation
    path('factures/', views.facture_list, name='facture_list'),
    path('factures/<int:commande_pk>/creer/', views.facture_create, name='facture_create'),
    path('factures/<int:pk>/detail/', views.facture_detail, name='facture_detail'),
    path('factures/<int:pk>/statut/', views.facture_update_statut, name='facture_update_statut'),
]
