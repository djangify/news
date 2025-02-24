# core/views.py
from django.shortcuts import render
from feeds.models import Content

def index(request, category=None):
    # Get content filtered by category if provided
    if category:
        content_list = Content.objects.filter(category__iexact=category).order_by('-published_date')
    else:
        content_list = Content.objects.all().order_by('-published_date')
    
    # Paginate the content
    content_list = content_list[:12]  # Show first 12 items, rest will load via AJAX
    
    context = {
        'content_list': content_list,
        'category': category,
    }
    # Using the template directly from the root templates directory
    return render(request, 'index.html', context)


def search(request):
    query = request.GET.get('q', '')
    content_list = Content.objects.filter(title__icontains=query).order_by('-published_date')
    
    context = {
        'content_list': content_list,
        'query': query,
    }
    return render(request, 'index.html', context)