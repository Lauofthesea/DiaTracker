"""
Retry logic for network failures with exponential backoff.
Implements up to 3 attempts with exponential backoff as per requirements.
"""

import asyncio
import logging
from typing import Callable, TypeVar, Optional, Type, Tuple
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts (default: 3)
            base_delay: Initial delay in seconds (default: 1.0)
            max_delay: Maximum delay in seconds (default: 10.0)
            exponential_base: Base for exponential backoff (default: 2.0)
            exceptions: Tuple of exception types to retry on
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.exceptions = exceptions


async def retry_async(
    func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """
    Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        *args: Positional arguments for the function
        config: Retry configuration (uses default if None)
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of the function call
        
    Raises:
        Last exception if all retries fail
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except config.exceptions as e:
            last_exception = e
            
            if attempt < config.max_attempts - 1:
                # Calculate delay with exponential backoff
                delay = min(
                    config.base_delay * (config.exponential_base ** attempt),
                    config.max_delay
                )
                
                logger.warning(
                    f"Attempt {attempt + 1}/{config.max_attempts} failed for {func.__name__}: {str(e)}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"All {config.max_attempts} attempts failed for {func.__name__}: {str(e)}"
                )
    
    # Raise the last exception if all retries failed
    raise last_exception


def retry_sync(
    func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """
    Retry a synchronous function with exponential backoff.
    
    Args:
        func: Function to retry
        *args: Positional arguments for the function
        config: Retry configuration (uses default if None)
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of the function call
        
    Raises:
        Last exception if all retries fail
    """
    import time
    
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            return func(*args, **kwargs)
        except config.exceptions as e:
            last_exception = e
            
            if attempt < config.max_attempts - 1:
                # Calculate delay with exponential backoff
                delay = min(
                    config.base_delay * (config.exponential_base ** attempt),
                    config.max_delay
                )
                
                logger.warning(
                    f"Attempt {attempt + 1}/{config.max_attempts} failed for {func.__name__}: {str(e)}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                time.sleep(delay)
            else:
                logger.error(
                    f"All {config.max_attempts} attempts failed for {func.__name__}: {str(e)}"
                )
    
    # Raise the last exception if all retries failed
    raise last_exception


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator for adding retry logic to async functions.
    
    Args:
        config: Retry configuration (uses default if None)
        
    Example:
        @with_retry(RetryConfig(max_attempts=3))
        async def fetch_data():
            # ... network call ...
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_async(func, *args, config=config, **kwargs)
        return wrapper
    return decorator
