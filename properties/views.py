from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Property
from .utils import get_all_properties, get_property_stats
import logging

logger = logging.getLogger(__name__)


@cache_page(60 * 15)  # Cache for 15 minutes (900 seconds)
def property_list(request):
    """
    View to display all properties with page-level caching.
    
    This view uses two levels of caching:
    1. Page-level caching (@cache_page) - caches the entire HTTP response for 15 minutes
    2. Low-level caching (get_all_properties) - caches the queryset for 1 hour
    
    The page cache is stored with a key that includes URL and query parameters,
    so different pages and filters are cached separately.
    """
    logger.info("Processing property_list view")
    
    # Use the cached queryset from utils.py
    properties = get_all_properties()
    
    # Get cached statistics
    stats = get_property_stats()
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(properties, 20)  # Show 20 properties per page
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'total_properties': stats['total_properties'],
        'avg_price': stats['avg_price'],
        'max_price': stats['max_price'],
        'min_price': stats['min_price'],
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'cache_info': {
            'page_cache_duration': '15 minutes',
            'queryset_cache_duration': '1 hour',
            'stats_cache_duration': '30 minutes',
        }
    }
    
    return render(request, 'properties/property_list.html', context)


def property_list_no_cache(request):
    """
    Property list view without any caching for comparison.
    
    This view can be used to compare performance with the cached version.
    """
    logger.info("Processing property_list_no_cache view (no caching)")
    
    # Direct database query without caching
    properties = Property.objects.all().order_by('-created_at')
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(properties, 20)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'total_properties': properties.count(),
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'cache_info': {
            'caching_enabled': False,
            'note': 'This view has no caching for performance comparison'
        }
    }
    
    return render(request, 'properties/property_list.html', context)


@cache_page(60 * 15)  # Cache for 15 minutes
def property_list_json(request):
    """
    JSON API view for properties list with caching.
    
    Returns property data in JSON format for API consumption.
    Uses both page-level and low-level caching.
    """
    logger.info("Processing property_list_json view")
    
    # Use cached queryset
    properties = get_all_properties()
    stats = get_property_stats()
    
    # Convert to list of dictionaries
    properties_data = []
    for property_obj in properties:
        properties_data.append({
            'id': property_obj.id if hasattr(property_obj, 'id') else None,
            'title': property_obj.title if hasattr(property_obj, 'title') else str(property_obj),
            'description': property_obj.description if hasattr(property_obj, 'description') else '',
            'price': str(property_obj.price) if hasattr(property_obj, 'price') else '0',
            'location': property_obj.location if hasattr(property_obj, 'location') else '',
            'created_at': property_obj.created_at.isoformat() if hasattr(property_obj, 'created_at') else '',
        })
    
    return JsonResponse({
        'properties': properties_data,
        'total_count': len(properties_data),
        'statistics': stats,
        'cache_info': {
            'page_cached': True,
            'queryset_cached': True,
            'cache_duration': '15 minutes (page), 1 hour (queryset)'
        }
    })


def property_detail(request, property_id):
    """
    View to display a single property detail.
    
    This view is not cached as individual property details
    may have user-specific content or change frequently.
    """
    try:
        property_obj = Property.objects.get(id=property_id)
        context = {
            'property': property_obj,
        }
        return render(request, 'properties/property_detail.html', context)
    except Property.DoesNotExist:
        context = {
            'error': 'Property not found',
        }
        return render(request, 'properties/property_not_found.html', context, status=404)
