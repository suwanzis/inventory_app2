from django.urls import path
from .views import register, user_login, user_logout, inventory_list, home

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('inventory/', inventory_list, name='inventory_list'),
]