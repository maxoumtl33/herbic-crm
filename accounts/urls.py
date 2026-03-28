from django.urls import path
from . import views
from .rapport_views import rapport_vendeurs
from .stats_views import page_statistiques

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('utilisateurs/', views.user_list, name='user_list'),
    path('utilisateurs/creer/', views.user_create, name='user_create'),
    path('utilisateurs/<int:pk>/modifier/', views.user_edit, name='user_edit'),
    path('utilisateurs/<int:pk>/toggle/', views.user_toggle_active, name='user_toggle_active'),
    path('journal/', views.journal_activite, name='journal'),
    path('rapports/vendeurs/', rapport_vendeurs, name='rapport_vendeurs'),
    path('statistiques/', page_statistiques, name='statistiques'),
]
