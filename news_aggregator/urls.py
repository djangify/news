from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from core.sitemap import StaticViewSitemap, ContentSitemap, CategorySitemap
from core.views import robots_txt
from django.views.static import serve

sitemaps = {
    'static': StaticViewSitemap,
    'content': ContentSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('feeds.urls')),  # maintains existing API endpoints
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'), 
        path('static/<path:path>', serve, {
        'document_root': settings.STATIC_ROOT,
    }),
    path('media/<path:path>', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
] 