from django.db import models
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

class RSSFeed(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    FEED_TYPES = [
        ('article', 'Article Feed'),
        ('youtube', 'YouTube Feed'),
    ]
    feed_type = models.CharField(max_length=10, choices=FEED_TYPES, default='article')
    
    # Add category choices
    CATEGORY_CHOICES = [
        ('ai', 'Artificial Intelligence'),
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('python', 'Python'),
        ('devops', 'DevOps'),
        ('news', 'News'),
        ('general', 'General'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="general")
    
    active = models.BooleanField(default=True)
    last_fetched = models.DateTimeField(null=True, blank=True)
    error_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def fetch_feed_content(self):
      """Manually trigger feed fetch"""
      from .services.feed_fetcher import FeedFetcher
      fetcher = FeedFetcher()
      fetcher.fetch_feed(self)

    def reset_error_count(self):
      """Reset the error counter"""
      self.error_count = 0
      self.save()

class Content(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField()
    url = models.URLField()
    image_url = models.URLField(max_length=2000, null=True, blank=True)
    source = models.ForeignKey(RSSFeed, on_delete=models.CASCADE)
    published_date = models.DateTimeField()
    is_pinned = models.BooleanField(default=False)
    category = models.CharField(max_length=50, null=True, blank=True, default="General")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source = models.ForeignKey('RSSFeed', on_delete=models.CASCADE, db_index=True) 
    

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-is_pinned', '-published_date']
        indexes = [
            models.Index(fields=['published_date', 'category']),  # Compound index for common queries
        ]

@receiver(post_save, sender=Content)
def clear_content_cache(sender, instance, **kwargs):
    # Clear cache when content is updated
    cache.delete('homepage_news_items')

