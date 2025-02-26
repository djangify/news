from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import RSSFeed, Content
from .serializers import RSSFeedSerializer, ContentSerializer

class ContentPagination(PageNumberPagination):
    page_size = 12  
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        next_url = None
        if self.page.has_next():
            # Explicitly construct the next URL
            page_number = self.page.next_page_number()
            request = self.request
            url = request.build_absolute_uri()
            
            # Handle existing query parameters
            if 'page=' in url:
                next_url = url.replace(f'page={self.page.number}', f'page={page_number}')
            elif '?' in url:
                next_url = f"{url}&page={page_number}"
            else:
                next_url = f"{url}?page={page_number}"
        
        return Response({
            'count': self.page.paginator.count,
            'next': next_url,
            'previous': self.get_previous_link(),
            'results': data
        })

@api_view(['GET'])
def load_more_content(request):
    """API endpoint for loading more content"""
    page = request.GET.get('page', 1)
    paginator = ContentPagination()
    queryset = Content.objects.all().order_by('-is_pinned', '-published_date')
    
    # Add category filtering
    category = request.GET.get('category', None)
    if category is not None:
        # Handle both direct category values and display names
        category_values = dict([(v.lower(), k) for k, v in RSSFeed.CATEGORY_CHOICES])
        search_category = category_values.get(category.lower(), category)
        queryset = queryset.filter(category__iexact=search_category)
    
    # Paginate queryset
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = ContentSerializer(paginated_queryset, many=True)
    
    return paginator.get_paginated_response(serializer.data)


class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentSerializer
    pagination_class = ContentPagination

    def get_queryset(self):
        queryset = Content.objects.all().order_by('-is_pinned', '-published_date')
        category = self.request.query_params.get('category', None)
        if category is not None:
            # Handle both direct category values and display names
            category_values = dict([(v.lower(), k) for k, v in RSSFeed.CATEGORY_CHOICES])
            search_category = category_values.get(category.lower(), category)
            queryset = queryset.filter(category__iexact=search_category)
        return queryset

# Frontend Views
def content_list(request):
    """Main page view showing the content grid"""
    context = {
        'category_choices': dict(RSSFeed.CATEGORY_CHOICES)
    }
    return render(request, 'feeds/content_list.html', context)

