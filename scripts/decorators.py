"""
Decorators for Cross-Cutting Concerns

This module provides reusable decorators for:
- Retry logic
- Performance timing
- Caching
- Error handling
- Logging
- Rate limiting
"""
import time
import logging
import hashlib
import json
from functools import wraps
from typing import Callable, Type, Tuple, Any, Optional, Dict
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)


# ============================================================================
# RETRY DECORATOR
# ============================================================================

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry
    
    Example:
        @retry(max_attempts=3, delay=2, exceptions=(requests.RequestException,))
        def fetch_data():
            return requests.get(url)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}",
                            exc_info=True
                        )
                        raise
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    
                    if on_retry:
                        on_retry(attempt, e)
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        
        return wrapper
    return decorator


# ============================================================================
# TIMING DECORATOR
# ============================================================================

def timed(log_level: str = "INFO", include_args: bool = False):
    """
    Time function execution and log results.
    
    Args:
        log_level: Logging level (INFO, DEBUG, WARNING)
        include_args: Whether to include function arguments in log
    
    Example:
        @timed(log_level="DEBUG", include_args=True)
        def process_dashboard(dashboard_id):
            return extract_data(dashboard_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                log_msg = f"{func_name} completed in {duration:.2f}s"
                if include_args and args:
                    # Only show first 2 args to avoid logging sensitive data
                    log_msg += f" (args={args[:2]})"
                
                getattr(logger, log_level.lower())(log_msg)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{func_name} failed after {duration:.2f}s: {e}")
                raise
        
        return wrapper
    return decorator


# ============================================================================
# CACHING DECORATOR
# ============================================================================

class TTLCache:
    """Time-based cache with expiration"""
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Tuple[Optional[Any], Optional[datetime]]:
        """Get cached value and timestamp"""
        with self._lock:
            if key in self._cache:
                return self._cache[key], self._timestamps[key]
            return None, None
    
    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set cached value with TTL"""
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = datetime.now() + timedelta(seconds=ttl)
    
    def is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        with self._lock:
            if key not in self._timestamps:
                return True
            return datetime.now() > self._timestamps[key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()


# Global cache instance
_ttl_cache = TTLCache()


def cache_with_ttl(ttl_seconds: int = 300, key_func: Optional[Callable] = None):
    """
    Cache function results with time-to-live.
    
    Args:
        ttl_seconds: Time to live in seconds (default 5 minutes)
        key_func: Optional function to generate cache key from args
    
    Example:
        @cache_with_ttl(ttl_seconds=600)  # Cache for 10 minutes
        def get_verticals():
            return expensive_api_call()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name and serialized args
                key_data = f"{func.__name__}:{args}:{kwargs}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Check cache
            if not _ttl_cache.is_expired(cache_key):
                cached_value, _ = _ttl_cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_value
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            _ttl_cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        # Expose cache management methods
        wrapper.cache_clear = _ttl_cache.clear
        
        return wrapper
    return decorator


# ============================================================================
# ERROR HANDLING DECORATOR
# ============================================================================

def handle_errors(
    default_return: Any = None,
    log_error: bool = True,
    reraise: bool = False,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Centralized error handling decorator.
    
    Args:
        default_return: Value to return on error
        log_error: Whether to log the error
        reraise: Whether to reraise the exception after handling
        exceptions: Tuple of exceptions to catch
    
    Example:
        @handle_errors(default_return={}, log_error=True)
        def fetch_dashboard(dashboard_id):
            return api.get_dashboard(dashboard_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log_error:
                    # Get limited context to avoid logging sensitive data
                    args_context = args[:2] if args else []
                    kwargs_context = list(kwargs.keys()) if kwargs else []
                    
                    logger.error(
                        f"Error in {func.__name__}: {e}",
                        exc_info=True,
                        extra={
                            'function': func.__name__,
                            'args_count': len(args),
                            'kwargs_keys': kwargs_context
                        }
                    )
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


# ============================================================================
# VALIDATION DECORATOR
# ============================================================================

def validate_args(**validators):
    """
    Validate function arguments using validator functions.
    
    Args:
        **validators: Dict mapping parameter names to validator functions
    
    Example:
        @validate_args(
            dashboard_id=lambda x: isinstance(x, int) and x > 0,
            chart_type=lambda x: x in ['bar', 'line', 'table']
        )
        def process_chart(dashboard_id, chart_type):
            return do_processing()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each argument
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Validation failed for {param_name}={value} "
                            f"in {func.__name__}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# RATE LIMITING DECORATOR
# ============================================================================

class RateLimiter:
    """Rate limiter using sliding window algorithm"""
    def __init__(self):
        self.calls: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, key: str, max_calls: int, period: int) -> bool:
        """Check if call is within rate limit"""
        with self.lock:
            now = time.time()
            # Remove old calls outside the window
            self.calls[key] = [t for t in self.calls[key] if now - t < period]
            
            if len(self.calls[key]) < max_calls:
                self.calls[key].append(now)
                return True
            return False


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(max_calls: int = 10, period: int = 60, key_func: Optional[Callable] = None):
    """
    Rate limit function calls using sliding window.
    
    Args:
        max_calls: Maximum calls allowed
        period: Time period in seconds
        key_func: Function to extract rate limit key from args
    
    Example:
        @rate_limit(max_calls=5, period=60)  # 5 calls per minute
        def expensive_llm_call():
            return call_claude_api()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = f"{func.__name__}:{key_func(*args, **kwargs)}"
            else:
                key = func.__name__
            
            if not _rate_limiter.is_allowed(key, max_calls, period):
                raise Exception(
                    f"Rate limit exceeded for {func.__name__}. "
                    f"Max {max_calls} calls per {period}s"
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# DEPRECATED DECORATOR
# ============================================================================

def deprecated(reason: str = "", alternative: str = ""):
    """
    Mark function as deprecated with warning.
    
    Args:
        reason: Why the function is deprecated
        alternative: What to use instead
    
    Example:
        @deprecated(reason="Old API", alternative="use new_api() instead")
        def old_api():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = f"{func.__name__} is deprecated"
            if reason:
                message += f": {reason}"
            if alternative:
                message += f". {alternative}"
            
            logger.warning(message)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

