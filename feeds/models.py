import asyncio
from django.db import models
from django.utils import timezone

class RSSFeed(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    FEED_TYPES = [
        ('ARTICLE', 'Article Feed'),
        ('YOUTUBE', 'YouTube Feed'),
    ]
    feed_type = models.CharField(max_length=10, choices=FEED_TYPES, default='ARTICLE')
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
      asyncio.run(fetcher.fetch_feed(self))

    def reset_error_count(self):
      """Reset the error counter"""
      self.error_count = 0
      self.save()

class Content(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField()
    url = models.URLField()
    image_url = models.URLField(null=True, blank=True)
    source = models.ForeignKey(RSSFeed, on_delete=models.CASCADE)
    published_date = models.DateTimeField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-is_pinned', '-published_date']


