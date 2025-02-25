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
        self.default_img = '/static/img/default_thumbnail.png'

    def fetch_feed(self, feed):
        """Fetch and process a single feed"""
        try:
            parsed_feed = feedparser.parse(feed.url)
            
            if hasattr(parsed_feed, 'bozo_exception') and parsed_feed.bozo_exception and not parsed_feed.entries:
                logger.error(f"Feed error for {feed.name}: {parsed_feed.bozo_exception}")
                feed.error_count += 1
                feed.save()
                return
            
            # Process entries if we have any, even if there was a bozo exception
            if not parsed_feed.entries:
                logger.error(f"No entries found in feed: {feed.name}")
                feed.error_count += 1
                feed.save()
                return
                
            for entry in parsed_feed.entries[:20]:  # Limit to latest 20 entries
                try:
                    # Skip if content already exists
                    if Content.objects.filter(url=entry.link).exists():
                        continue

                    image_url = None
                    if feed.feed_type == 'youtube':
                        video_id = self.get_youtube_video_id(entry.link)
                        image_url = self.get_youtube_thumbnail(video_id)
                    else:
                        # Try to find image in entry
                        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                            image_url = entry.media_thumbnail[0]['url']
                        elif hasattr(entry, 'media_content') and entry.media_content:
                            image_url = entry.media_content[0]['url']
                    
                    # Try to extract an image from enclosures if available
                    if not image_url and hasattr(entry, 'enclosures'):
                        for enclosure in entry.enclosures:
                            if enclosure.get('type', '').startswith('image/'):
                                image_url = enclosure.get('href')
                                break
                    
                    # Use the feed's category directly
                    category = feed.category

                    # Get description from either summary or content
                    description = ''
                    if hasattr(entry, 'summary'):
                        description = entry.summary
                    elif hasattr(entry, 'content') and entry.content:
                        description = entry.content[0].value
                    
                    # Clean description - remove problematic characters if needed
                    description = self.clean_text(description)
                    
                    # Truncate image_url if too long (MySQL has a limit)
                    if image_url and len(image_url) > 1990:
                        image_url = image_url[:1990]
                    
                    # Get published date
                    published_date = self.parse_date(
                        entry.get('published', entry.get('updated', timezone.now()))
                    )

                    Content.objects.create(
                        title=self.clean_text(entry.title),
                        description=description,
                        url=entry.link,
                        image_url=image_url or self.default_img,
                        source=feed,
                        category=category,
                        published_date=published_date
                    )
                except Exception as e:
                    # Log the error but continue processing other entries
                    logger.error(f"Error processing entry {entry.get('title', 'Unknown')}: {str(e)}")
                    continue

            feed.last_fetched = timezone.now()
            feed.error_count = 0
            feed.save()

        except Exception as e:
            logger.error(f"Error fetching feed {feed.name}: {str(e)}")
            feed.error_count += 1
            feed.save()

    def clean_text(self, text):
        """Clean text to remove problematic characters."""
        if not text:
            return ""
        # Replace emojis and other problematic characters if needed
        return text.encode('utf-8', errors='ignore').decode('utf-8')

    def parse_date(self, date_str):
        """Parse date string from feed to datetime object"""
        if not date_str:
            return timezone.now()
        
        try:
            dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        except ValueError:
            try:
                dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
            except ValueError:
                try:
                    dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                except ValueError:
                    return timezone.now()
        
        return dt
    
    def get_youtube_video_id(self, url):
        """Extract video ID from YouTube URL"""
        parsed_url = urlparse(url)
        if parsed_url.netloc in ['www.youtube.com', 'youtube.com']:
            query = parse_qs(parsed_url.query)
            return query.get('v', [''])[0]
        elif parsed_url.netloc in ['youtu.be']:
            return parsed_url.path.lstrip('/')
        return ''
    
    def get_youtube_thumbnail(self, video_id):
        """Get thumbnail URL for YouTube video"""
        if not video_id:
            return None
        return f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'