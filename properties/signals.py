"""
Django signals for automatic cache invalidation.

This module contains signal handlers that automatically invalidate
the Redis cache when Property objects are created, updated, or deleted.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Property)
def invalidate_property_cache_on_save(sender, instance, created, **kwargs):
    """
    Signal handler for Property post_save.
    
    This handler is triggered when a Property object is saved (created or updated).
    It invalidates the 'all_properties' cache to ensure data consistency.
    
    Args:
        sender: The model class (Property)
        instance: The actual Property instance being saved
        created: Boolean indicating if this is a new object
        **kwargs: Additional keyword arguments
    """
    cache_key = 'all_properties'
    
    # Delete the cached queryset
    cache.delete(cache_key)
    
    # Also delete related cache keys
    cache.delete('property_stats')
    
    # Log the cache invalidation
    action = "created" if created else "updated"
    logger.info(
        f"Property {action}: '{instance.title}' (ID: {instance.id}). "
        f"Invalidated cache key: {cache_key}"
    )


@receiver(post_delete, sender=Property)
def invalidate_property_cache_on_delete(sender, instance, **kwargs):
    """
    Signal handler for Property post_delete.
    
    This handler is triggered when a Property object is deleted.
    It invalidates the 'all_properties' cache to ensure data consistency.
    
    Args:
        sender: The model class (Property)
        instance: The actual Property instance being deleted
        **kwargs: Additional keyword arguments
    """
    cache_key = 'all_properties'
    
    # Delete the cached queryset
    cache.delete(cache_key)
    
    # Also delete related cache keys
    cache.delete('property_stats')
    
    # Log the cache invalidation
    logger.info(
        f"Property deleted: '{instance.title}' (ID: {instance.id}). "
        f"Invalidated cache key: {cache_key}"
    )


def invalidate_all_property_caches():
    """
    Utility function to manually invalidate all property-related caches.
    
    This can be called manually when needed to clear all property caches.
    """
    cache_keys = [
        'all_properties',
        'property_stats',
    ]
    
    # Also invalidate location-based caches (pattern-based deletion)
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        
        # Get all keys that match property location pattern
        location_keys = redis_conn.keys("property_listings:1:properties_location_*")
        if location_keys:
            cache_keys.extend([key.decode('utf-8').replace('property_listings:1:', '') for key in location_keys])
    except Exception as e:
        logger.warning(f"Could not get location cache keys: {e}")
    
    # Delete all cache keys
    cache.delete_many(cache_keys)
    
    logger.info(f"Manually invalidated {len(cache_keys)} property cache keys")


# Additional signal handlers for bulk operations
@receiver(post_save, sender=Property)
def log_property_changes(sender, instance, created, **kwargs):
    """
    Additional signal handler to log property changes for debugging.
    
    This handler logs all property changes which can be useful for
    debugging cache invalidation issues.
    """
    action = "CREATED" if created else "UPDATED"
    logger.debug(
        f"[PROPERTY {action}] "
        f"Title: {instance.title}, "
        f"Price: ${instance.price}, "
        f"Location: {instance.location}"
    )
