# feeds/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('category/<str:category>/', views.index, name='category'),
    path('search/', views.search, name='search'), 
]