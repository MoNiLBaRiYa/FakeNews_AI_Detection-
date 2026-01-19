"""Performance monitoring utilities."""
import time
import logging
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)

def measure_time(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.
    
    Usage:
        @measure_time
        def my_function():
            # code here
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    
    Usage:
        @retry_on_failure(max_retries=3, delay=2.0)
        def my_function():
            # code that might fail
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            
            logger.error(f"{func.__name__} failed after {max_retries} attempts")
            raise last_exception
        
        return wrapper
    return decorator

class PerformanceMonitor:
    """Monitor application performance metrics."""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'total_predictions': 0,
            'total_errors': 0,
            'avg_response_time': 0.0,
            'response_times': []
        }
    
    def record_request(self, response_time: float):
        """Record a request."""
        self.metrics['total_requests'] += 1
        self.metrics['response_times'].append(response_time)
        
        # Keep only last 1000 response times
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
        
        # Calculate average
        self.metrics['avg_response_time'] = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
    
    def record_prediction(self):
        """Record a prediction."""
        self.metrics['total_predictions'] += 1
    
    def record_error(self):
        """Record an error."""
        self.metrics['total_errors'] += 1
    
    def get_metrics(self) -> dict:
        """Get current metrics."""
        return {
            'total_requests': self.metrics['total_requests'],
            'total_predictions': self.metrics['total_predictions'],
            'total_errors': self.metrics['total_errors'],
            'avg_response_time': round(self.metrics['avg_response_time'], 4),
            'error_rate': round(
                (self.metrics['total_errors'] / self.metrics['total_requests'] * 100)
                if self.metrics['total_requests'] > 0 else 0,
                2
            )
        }
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = {
            'total_requests': 0,
            'total_predictions': 0,
            'total_errors': 0,
            'avg_response_time': 0.0,
            'response_times': []
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()
