from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemap import StaticViewSitemap, ContentSitemap, CategorySitemap
from core.views import robots_txt

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
    path('accounts/', include('allauth.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)