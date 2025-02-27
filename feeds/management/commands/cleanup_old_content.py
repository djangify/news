# feeds/management/commands/cleanup_old_content.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Exists, OuterRef
from feeds.models import Content, Favorite


class Command(BaseCommand):
    help = 'Remove content older than a specified number of days unless favorited'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=60, help='Number of days to keep content')

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Keep pinned content and favorited content
        has_favorites = Favorite.objects.filter(content=OuterRef('pk')).exists()
        
        old_content = Content.objects.filter(
            published_date__lt=cutoff_date,
            is_pinned=False
        ).annotate(
            is_favorited=Exists(Favorite.objects.filter(content=OuterRef('pk')))
        ).filter(
            is_favorited=False
        )
        
        count = old_content.count()
        old_content.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully removed {count} content items older than {days} days (excluding favorites)')
        )
