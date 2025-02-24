# feeds/services/feed_fetcher.py

import feedparser
import logging
from datetime import datetime
from django.utils import timezone
from urllib.parse import urlparse, parse_qs
from ..models import RSSFeed, Content

logger = logging.getLogger(__name__)

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
            
            # Determine category based on tags or feed name
            category = "General"
            if hasattr(entry, 'tags') and entry.tags:
                for tag in entry.tags:
                    tag_name = tag.get('term', '').lower()
                    if 'tech' in tag_name or 'technology' in tag_name:
                        category = 'tech'
                        break
                    elif 'dev' in tag_name or 'developer' in tag_name or 'programming' in tag_name:
                        category = 'dev'
                        break
                    elif 'ai' in tag_name or 'artificial intelligence' in tag_name or 'machine learning' in tag_name:
                        category = 'ai'
                        break
            
            # If no category from tags, try feed name
            if category == "General":
                feed_name_lower = feed.name.lower()
                if 'tech' in feed_name_lower:
                    category = 'tech'
                elif 'dev' in feed_name_lower or 'code' in feed_name_lower:
                    category = 'dev'
                elif 'ai' in feed_name_lower or 'intelligence' in feed_name_lower:
                    category = 'ai'

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