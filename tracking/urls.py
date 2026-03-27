from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    path('culture/<int:culture_pk>/', views.suivi_list, name='suivi_list'),
    path('culture/<int:culture_pk>/ajouter/', views.suivi_create, name='suivi_create'),
    path('<int:pk>/modifier/', views.suivi_edit, name='suivi_edit'),
    path('culture/<int:culture_pk>/stats/', views.stats_edit, name='stats_edit'),
]
