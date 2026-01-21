"""
Performance monitoring for the web application
"""
import time
import logging
from functools import wraps
from collections import defaultdict, deque
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Performance metrics storage
_performance_metrics = {
    'request_times': defaultdict(deque),
    'endpoint_counts': defaultdict(int),
    'error_counts': defaultdict(int),
    'slow_requests': deque(maxlen=100),
}


def monitor_performance(f):
    """Decorator to monitor function performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        endpoint = f.__name__
        
        try:
            result = f(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # Record metrics
            _performance_metrics['request_times'][endpoint].append(elapsed)
            _performance_metrics['endpoint_counts'][endpoint] += 1
            
            # Keep only last 100 timings per endpoint
            if len(_performance_metrics['request_times'][endpoint]) > 100:
                _performance_metrics['request_times'][endpoint].popleft()
            
            # Log slow requests
            if elapsed > 1.0:  # More than 1 second
                _performance_metrics['slow_requests'].append({
                    'endpoint': endpoint,
                    'elapsed': elapsed,
                    'timestamp': datetime.now().isoformat()
                })
                logger.warning(f"Slow request: {endpoint} took {elapsed:.2f}s")
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            _performance_metrics['error_counts'][endpoint] += 1
            logger.error(f"Error in {endpoint} after {elapsed:.2f}s: {str(e)}")
            raise
    
    return decorated_function


def get_performance_stats():
    """Get performance statistics"""
    stats = {}
    
    for endpoint, times in _performance_metrics['request_times'].items():
        if times:
            stats[endpoint] = {
                'count': _performance_metrics['endpoint_counts'][endpoint],
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'errors': _performance_metrics['error_counts'][endpoint],
            }
    
    return stats


def get_slow_requests(limit=10):
    """Get recent slow requests"""
    return list(_performance_metrics['slow_requests'])[-limit:]


def reset_performance_metrics():
    """Reset all performance metrics"""
    global _performance_metrics
    _performance_metrics = {
        'request_times': defaultdict(deque),
        'endpoint_counts': defaultdict(int),
        'error_counts': defaultdict(int),
        'slow_requests': deque(maxlen=100),
    }


# Performance monitor instance
performance_monitor = {
    'get_stats': get_performance_stats,
    'get_slow_requests': get_slow_requests,
    'reset': reset_performance_metrics,
}
