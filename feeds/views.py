from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import RSSFeed, Content
from .serializers import RSSFeedSerializer, ContentSerializer

class ContentPagination(PageNumberPagination):
    page_size = 54  # 3 across, 18 down as requested
    page_size_query_param = 'page_size'
    max_page_size = 100

class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Content.objects.all().order_by('-is_pinned', '-published_date')
    serializer_class = ContentSerializer
    pagination_class = ContentPagination

# Frontend Views
def content_list(request):
    """Main page view showing the content grid"""
    return render(request, 'feeds/content_list.html')

@api_view(['GET'])
def load_more_content(request):
    """API endpoint for loading more content"""
    page = request.GET.get('page', 1)
    paginator = ContentPagination()
    queryset = Content.objects.all().order_by('-is_pinned', '-published_date')
    
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = ContentSerializer(paginated_queryset, many=True)
    
    return paginator.get_paginated_response(serializer.data)