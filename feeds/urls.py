from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'content', views.ContentViewSet, basename='content')

urlpatterns = [
    # Frontend URL
    path('all/', views.content_list, name='content_list'),
    
    # API URLs
    path('api/load-more/', views.load_more_content, name='load_more_content'),
] + router.urls