"""
Factory Pattern - Centralized object creation

This module provides factory classes for creating complex objects with
all their dependencies properly configured.
"""
from typing import Optional, Dict, Any
import logging

try:
    from settings import AppSettings, get_settings
    from repositories import IDashboardRepository, FileSystemDashboardRepository
    from events import EventBus, get_event_bus
except ImportError:
    from scripts.settings import AppSettings, get_settings
    from scripts.repositories import IDashboardRepository, FileSystemDashboardRepository
    from scripts.events import EventBus, get_event_bus

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Factory for creating service instances with proper configuration.
    
    This centralizes object creation and dependency management.
    """
    
    def __init__(self, settings: Optional[AppSettings] = None):
        """
        Initialize factory.
        
        Args:
            settings: Application settings. If None, uses global settings.
        """
        self.settings = settings or get_settings()
        self._cache: Dict[str, Any] = {}
        self._event_bus = get_event_bus()
    
    def create_dashboard_repository(self) -> IDashboardRepository:
        """
        Create dashboard repository.
        
        Returns:
            Configured dashboard repository
        """
        if 'dashboard_repository' not in self._cache:
            logger.debug("Creating dashboard repository")
            self._cache['dashboard_repository'] = FileSystemDashboardRepository(
                base_dir=self.settings.base_dir
            )
        return self._cache['dashboard_repository']
    
    def create_superset_extractor(self):
        """
        Create Superset API extractor.
        
        Returns:
            Configured SupersetExtractor
        """
        from query_extract import SupersetExtractor
        
        if 'superset_extractor' not in self._cache:
            logger.debug("Creating Superset extractor")
            headers = {
                'Cookie': self.settings.superset_cookie,
                'X-CSRFToken': self.settings.superset_csrf_token
            }
            self._cache['superset_extractor'] = SupersetExtractor(
                base_url=self.settings.superset_base_url,
                headers=headers
            )
        return self._cache['superset_extractor']
    
    def create_progress_tracker(self):
        """
        Create progress tracker.
        
        Returns:
            Configured ProgressTracker
        """
        from progress_tracker import ProgressTracker
        
        if 'progress_tracker' not in self._cache:
            logger.debug("Creating progress tracker")
            self._cache['progress_tracker'] = ProgressTracker(
                progress_file=str(self.settings.progress_file)
            )
        return self._cache['progress_tracker']
    
    def get_event_bus(self) -> EventBus:
        """
        Get event bus instance.
        
        Returns:
            EventBus instance
        """
        return self._event_bus
    
    def clear_cache(self) -> None:
        """Clear cached instances (useful for testing)"""
        self._cache.clear()


# Global factory instance
_factory: Optional[ServiceFactory] = None


def get_factory(settings: Optional[AppSettings] = None) -> ServiceFactory:
    """
    Get the global factory instance.
    
    Args:
        settings: Optional settings to use. If None, uses global settings.
    
    Returns:
        ServiceFactory instance
    """
    global _factory
    if _factory is None:
        _factory = ServiceFactory(settings)
    return _factory


def reset_factory() -> None:
    """Reset factory (useful for testing)"""
    global _factory
    _factory = None

