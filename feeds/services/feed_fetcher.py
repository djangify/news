# feeds/services/feed_fetcher.py

import feedparser
import logging
from datetime import datetime
from django.utils import timezone
from urllib.parse import urlparse, parse_qs
from ..models import RSSFeed, Content

logger = logging.getLogger(__name__)

# Change this section in feeds/services/feed_fetcher.py
def fetch_feed(self, feed: RSSFeed):
    """Fetch and process a single feed"""
    try:
        parsed_feed = feedparser.parse(feed.url)
        
        if parsed_feed.bozo:
            logger.error(f"Feed error for {feed.name}: {parsed_feed.bozo_exception}")
            feed.error_count += 1
            feed.save()
            return
        
        for entry in parsed_feed.entries[:20]:  # Limit to latest 20 entries
            # Skip if content already exists
            if Content.objects.filter(url=entry.link).exists():
                continue

            image_url = None
            if feed.feed_type == 'YOUTUBE':
                video_id = self.get_youtube_video_id(entry.link)
                image_url = self.get_youtube_thumbnail(video_id)
            else:
                # Try to find image in entry
                if hasattr(entry, 'media_thumbnail'):
                    image_url = entry.media_thumbnail[0]['url']
                elif hasattr(entry, 'media_content'):
                    image_url = entry.media_content[0]['url']
            
            # Use the feed's category directly
            category = feed.category

            Content.objects.create(
                title=entry.title,
                description=entry.summary if hasattr(entry, 'summary') else '',
                url=entry.link,
                image_url=image_url or self.default_img,
                source=feed,
                category=category,
                published_date=self.parse_date(
                    entry.get('published', entry.get('updated', None))
                )
            )

        feed.last_fetched = timezone.now()
        feed.error_count = 0
        feed.save()

    except Exception as e:
        logger.error(f"Error fetching feed {feed.name}: {str(e)}")
        feed.error_count += 1
        feed.save()
