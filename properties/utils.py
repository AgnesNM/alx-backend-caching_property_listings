"""
Utility functions for property caching.
"""

from django.core.cache import cache
from .models import Property
import logging

logger = logging.getLogger(__name__)


def get_all_properties():
    """
    Retrieve all properties with caching.
    
    This function implements a cache-aside pattern:
    1. Check Redis for cached queryset using 'all_properties' key
    2. If not found, fetch from database using Property.objects.all()
    3. Store the queryset in Redis with 1 hour timeout (3600 seconds)
    4. Return the queryset
    
    Returns:
        QuerySet: All Property objects ordered by creation date
    """
    cache_key = 'all_properties'
    
    # Try to get the queryset from cache
    properties = cache.get(cache_key)
    
    if properties is not None:
        logger.info(f"Cache HIT for key: {cache_key}")
        return properties
    
    # Cache miss - fetch from database
    logger.info(f"Cache MISS for key: {cache_key}")
    properties = Property.objects.all().order_by('-created_at')
    
    # Convert to list to make it serializable for cache storage
    properties_list = list(properties)
    
    # Store in cache for 1 hour (3600 seconds)
    cache.set(cache_key, properties_list, 3600)
    logger.info(f"Cached {len(properties_list)} properties for 1 hour")
    
    return properties_list


def invalidate_property_cache():
    """
    Invalidate the property cache.
    
    This function should be called when properties are created, updated, or deleted
    to ensure cache consistency.
    """
    cache_key = 'all_properties'
    cache.delete(cache_key)
    logger.info(f"Invalidated cache for key: {cache_key}")


def get_property_stats():
    """
    Get cached property statistics.
    
    Returns basic statistics about properties with caching.
    Cache timeout: 30 minutes (1800 seconds)
    """
    cache_key = 'property_stats'
    
    stats = cache.get(cache_key)
    
    if stats is not None:
        logger.info(f"Cache HIT for property stats")
        return stats
    
    # Calculate stats from database
    logger.info(f"Cache MISS for property stats - calculating from database")
    
    total_properties = Property.objects.count()
    if total_properties > 0:
        avg_price = Property.objects.aggregate(
            avg_price=models.Avg('price')
        )['avg_price']
        max_price = Property.objects.aggregate(
            max_price=models.Max('price')
        )['max_price']
        min_price = Property.objects.aggregate(
            min_price=models.Min('price')
        )['min_price']
    else:
        avg_price = max_price = min_price = 0
    
    stats = {
        'total_properties': total_properties,
        'avg_price': float(avg_price) if avg_price else 0,
        'max_price': float(max_price) if max_price else 0,
        'min_price': float(min_price) if min_price else 0,
    }
    
    # Cache for 30 minutes
    cache.set(cache_key, stats, 1800)
    logger.info(f"Cached property statistics for 30 minutes")
    
    return stats


def get_properties_by_location(location):
    """
    Get properties filtered by location with caching.
    
    Args:
        location (str): Location to filter by
        
    Returns:
        list: Properties in the specified location
    """
    cache_key = f'properties_location_{location.lower().replace(" ", "_")}'
    
    properties = cache.get(cache_key)
    
    if properties is not None:
        logger.info(f"Cache HIT for location: {location}")
        return properties
    
    logger.info(f"Cache MISS for location: {location}")
    
    properties = list(
        Property.objects.filter(location__icontains=location).order_by('-created_at')
    )
    
    # Cache for 15 minutes
    cache.set(cache_key, properties, 900)
    logger.info(f"Cached {len(properties)} properties for location '{location}'")
    
    return properties
