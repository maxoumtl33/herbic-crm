from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Produits
    path('', views.produit_list, name='produit_list'),
    path('<int:pk>/', views.produit_detail, name='produit_detail'),
    path('creer/', views.produit_create, name='produit_create'),
    path('<int:pk>/modifier/', views.produit_edit, name='produit_edit'),
    path('<int:pk>/supprimer/', views.produit_delete, name='produit_delete'),
    # Catégories
    path('categories/', views.categorie_list, name='categorie_list'),
    path('categories/creer/', views.categorie_create, name='categorie_create'),
    path('categories/<int:pk>/modifier/', views.categorie_edit, name='categorie_edit'),
    path('categories/<int:pk>/supprimer/', views.categorie_delete, name='categorie_delete'),
    # Recommandations
    path('recommandations/', views.recommandation_list, name='recommandation_list'),
    path('recommandations/creer/', views.recommandation_create, name='recommandation_create'),
    path('recommandations/<int:pk>/modifier/', views.recommandation_edit, name='recommandation_edit'),
    path('recommandations/<int:pk>/supprimer/', views.recommandation_delete, name='recommandation_delete'),
]
