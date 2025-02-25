# core/views.py
from django.shortcuts import render
from feeds.models import Content, RSSFeed

def get_all_categories():
    """Get all unique categories from the RSSFeed model with their display names"""
    # Get unique categories directly from CATEGORY_CHOICES
    # But only include ones that are actually in use
    used_categories = set(RSSFeed.objects.values_list('category', flat=True).distinct())
    
    # Return a list of tuples (value, display_name) for each category that's in use
    return [(cat_value, cat_display) for cat_value, cat_display in RSSFeed.CATEGORY_CHOICES 
            if cat_value in used_categories]

def index(request, category=None):
    # Get all unique categories for navigation
    all_categories = get_all_categories()
    
    # Get content filtered by category if provided
    if category:
        content_list = Content.objects.filter(category__iexact=category).order_by('-published_date')
    else:
        content_list = Content.objects.all().order_by('-published_date')
    
    # Paginate the content - first 12 items only, rest loaded via AJAX
    content_list = content_list[:12]
    
    # Create a single context with all needed variables
    context = {
        'content_list': content_list,
        'all_categories': all_categories,
        'category': category,  # Keep this to highlight the current category
        'category_choices': dict(RSSFeed.CATEGORY_CHOICES)  # Add the choices dictionary
    }
    
    # Only one return statement
    return render(request, 'index.html', context)

def search(request):
    query = request.GET.get('q', '')
    content_list = Content.objects.filter(title__icontains=query).order_by('-published_date')
    all_categories = get_all_categories()
    
    context = {
        'content_list': content_list,
        'query': query,
        'all_categories': all_categories,
        'category_choices': dict(RSSFeed.CATEGORY_CHOICES)  # Add the choices dictionary
    }
    return render(request, 'index.html', context)
