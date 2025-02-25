# feeds/management/commands/fetch_feeds.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from feeds.models import RSSFeed
from feeds.services.feed_fetcher import FeedFetcher
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch all active RSS feeds'

    def handle(self, *args, **options):
        fetcher = FeedFetcher()
        active_feeds = RSSFeed.objects.filter(active=True)

        if not active_feeds:
            self.stdout.write(self.style.WARNING('No active feeds found'))
            return

        for feed in active_feeds:
            try:
                fetcher.fetch_feed(feed)  # Pass the feed object, not self
                self.stdout.write(self.style.SUCCESS(f'Successfully fetched: {feed.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error fetching {feed.name}: {str(e)}'))