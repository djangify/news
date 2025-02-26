# feeds/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('category/<str:category>/', views.index, name='category'),
    path('search/', views.search, name='search'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-policy/', views.terms_policy, name='terms_policy'),
]