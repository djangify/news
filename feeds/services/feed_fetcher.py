# feeds/services/feed_fetcher.py

import feedparser
import logging
from datetime import datetime
from django.utils import timezone
from urllib.parse import urlparse, parse_qs
from ..models import RSSFeed, Content

logger = logging.getLogger(__name__)

class FeedFetcher:
    def __init__(self):
        self.default_img = 'default_thumbnail.jpg'  # You'll need to add this image to your media folder

    def get_youtube_video_id(self, url):
        """Extract video ID from YouTube URL"""
        parsed_url = urlparse(url)
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        return None

    def get_youtube_thumbnail(self, video_id):
        """Get YouTube thumbnail URL"""
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        return None

    def parse_date(self, date_str):
        """Parse date from feed to Django timezone-aware datetime"""
        if not date_str:
            return timezone.now()
        try:
            parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return timezone.make_aware(parsed_date)
        except (ValueError, AttributeError):
            try:
                parsed_date = feedparser._parse_date(date_str)
                return timezone.make_aware(datetime(*parsed_date[:6]))
            except:
                return timezone.now()

    async def fetch_feed(self, feed: RSSFeed):
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

                Content.objects.create(
                    title=entry.title,
                    description=entry.summary if hasattr(entry, 'summary') else '',
                    url=entry.link,
                    image_url=image_url or self.default_img,
                    source=feed,
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