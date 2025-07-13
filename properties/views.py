from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from .models import Property


@cache_page(60 * 15)  # Cache for 15 minutes (900 seconds)
def property_list(request):
    """
    View to display all properties with caching enabled.
    
    This view is cached in Redis for 15 minutes to improve performance.
    The cache key includes the URL and any query parameters.
    """
    # Get all properties ordered by creation date (newest first)
    properties = Property.objects.all().order_by('-created_at')
    
    # Optional: Add pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(properties, 20)  # Show 20 properties per page
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'total_properties': properties.count(),
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'properties/property_list.html', context)


@cache_page(60 * 15)  # Cache for 15 minutes
def property_list_json(request):
    """
    JSON API view for properties list with caching.
    
    Returns property data in JSON format for API consumption.
    Cached in Redis for 15 minutes.
    """
    properties = Property.objects.all().order_by('-created_at')
    
    # Convert to list of dictionaries
    properties_data = []
    for property_obj in properties:
        properties_data.append({
            'id': property_obj.id,
            'title': property_obj.title,
            'description': property_obj.description,
            'price': str(property_obj.price),
            'location': property_obj.location,
            'created_at': property_obj.created_at.isoformat(),
            'updated_at': property_obj.updated_at.isoformat(),
        })
    
    return JsonResponse({
        'properties': properties_data,
        'total_count': len(properties_data),
        'cached': True,  # Indicates this response is cached
    })


# Class-based view alternative with caching
@method_decorator(cache_page(60 * 15), name='dispatch')
class PropertyListView(ListView):
    """
    Class-based view for property list with caching.
    
    Alternative implementation using Django's ListView.
    The entire view is cached for 15 minutes.
    """
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 20
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_properties'] = Property.objects.count()
        return context


def property_detail(request, property_id):
    """
    View to display a single property detail.
    
    Note: This view is not cached as individual property details
    may change more frequently and have user-specific content.
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


# Cache management utilities
def clear_property_list_cache():
    """
    Utility function to clear the property list cache.
    
    This can be called when properties are added, updated, or deleted
    to ensure the cached list stays current.
    """
    from django.core.cache import cache
    from django.core.cache.utils import make_template_fragment_key
    
    # Clear the cache for the property list view
    cache_key = make_template_fragment_key('property_list')
    cache.delete(cache_key)
    
    # Also clear any related cache keys
    cache.delete_many([
        'property_list_page_1',
        'property_list_json',
        'property_count',
    ])
