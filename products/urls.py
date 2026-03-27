from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.produit_list, name='produit_list'),
    path('<int:pk>/', views.produit_detail, name='produit_detail'),
    path('creer/', views.produit_create, name='produit_create'),
    path('<int:pk>/modifier/', views.produit_edit, name='produit_edit'),
]
