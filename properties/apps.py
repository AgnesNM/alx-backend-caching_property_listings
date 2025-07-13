from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    """
    Application configuration for the properties app.
    
    This configuration class handles the setup of the properties app,
    including importing signal handlers for automatic cache invalidation.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'
    verbose_name = 'Property Listings'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        
        This method is called when Django starts up and the app registry
        is fully populated. It's the correct place to import signal handlers
        to ensure they are connected properly.
        """
        try:
            # Import signal handlers to register them
            from . import signals
            
            # Log that signals have been imported
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Property app signals have been imported and registered")
            
        except ImportError as e:
            # Log any import errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to import property signals: {e}")
            raise
