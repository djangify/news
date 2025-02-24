from django.contrib import admin
from .models import RSSFeed, Content

@admin.register(RSSFeed)
class RSSFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'feed_type', 'active', 'last_fetched', 'error_count')
    list_filter = ('feed_type', 'active')
    search_fields = ('name', 'url')

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_date', 'is_pinned')
    list_filter = ('source', 'is_pinned', 'published_date')
    search_fields = ('title', 'description')
    actions = ['pin_content', 'unpin_content']

    def pin_content(self, request, queryset):
        queryset.update(is_pinned=True)
    pin_content.short_description = "Pin selected content"

    def unpin_content(self, request, queryset):
        queryset.update(is_pinned=False)
    unpin_content.short_description = "Unpin selected content"