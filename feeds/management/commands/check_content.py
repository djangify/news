from django.core.management.base import BaseCommand
from feeds.models import Content, RSSFeed

class Command(BaseCommand):
    help = 'Check content in the database'

    def handle(self, *args, **options):
        content_count = Content.objects.count()
        feed_count = RSSFeed.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'Found {content_count} content items'))
        self.stdout.write(self.style.SUCCESS(f'Found {feed_count} RSS feeds'))
        
        if content_count > 0:
            self.stdout.write('\nRecent content:')
            for item in Content.objects.order_by('-published_date')[:5]:
                self.stdout.write(f"- {item.title} ({item.source.name}, {item.published_date})")
        
        if feed_count > 0:
            self.stdout.write('\nActive feeds:')
            for feed in RSSFeed.objects.filter(active=True):
                self.stdout.write(f"- {feed.name} (Category: {feed.get_category_display()})")
                