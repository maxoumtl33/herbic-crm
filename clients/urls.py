from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('<int:pk>/', views.client_detail, name='client_detail'),
    path('creer/', views.client_create, name='client_create'),
    path('<int:pk>/modifier/', views.client_edit, name='client_edit'),
    path('<int:client_pk>/culture/ajouter/', views.culture_create, name='culture_create'),
    path('culture/<int:pk>/modifier/', views.culture_edit, name='culture_edit'),
    path('culture/<int:culture_pk>/arrosage/ajouter/', views.produit_arrosage_create, name='produit_arrosage_create'),
    # Types de culture (directeur)
    path('types-culture/', views.type_culture_list, name='type_culture_list'),
    path('types-culture/creer/', views.type_culture_create, name='type_culture_create'),
    path('types-culture/<int:pk>/modifier/', views.type_culture_edit, name='type_culture_edit'),
    path('types-culture/<int:pk>/supprimer/', views.type_culture_delete, name='type_culture_delete'),
]
