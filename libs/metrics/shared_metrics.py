# shared_metrics.py
"""
Singleton wrapper for AWS Metrics Library
Ensures one metrics instance is shared across all modules
"""

import threading

from libs.metrics.aws_metrics import create_metrics_logger

class SingletonMetrics:
    """Singleton metrics logger"""
    _instance = None
    _lock = threading.Lock()
    _metrics = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def init(self, service_name: str, **kwargs):
        """Initialize metrics once"""
        if self._metrics is None:
            self._metrics = create_metrics_logger(service_name, **kwargs)
        return self._metrics

    def shutdown(self):
        """Shutdown metrics and allow re-initialization"""
        if self._metrics:
            self._metrics.flush_async_metrics()
            self._metrics.shutdown()
            self._metrics = None

    def __getattr__(self, name):
        """Forward all calls to the underlying metrics object"""
        if self._metrics is None:
            raise RuntimeError("Call init() first!")
        return getattr(self._metrics, name)

# Global instance
metrics = SingletonMetrics()

# Usage example:
if __name__ == "__main__":
    # Initialize once in your main script
    metrics.init("my-service", version="1.0.0")
    
    # Use anywhere
    metrics.log_event("test", {"key": "value"})
    metrics.increment_counter("requests")
    
    with metrics.time_operation("test_op"):
        import time
        time.sleep(0.1)
    
    metrics.shutdown()