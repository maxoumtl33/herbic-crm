from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('utilisateurs/', views.user_list, name='user_list'),
    path('utilisateurs/creer/', views.user_create, name='user_create'),
]
