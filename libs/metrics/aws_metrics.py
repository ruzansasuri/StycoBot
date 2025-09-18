"""
AWS Hybrid Metrics Library

A comprehensive metrics collection library for AWS applications that provides:
1. Structured logging to CloudWatch Logs
2. Critical metrics to CloudWatch Metrics  
3. Detailed async metrics via SQS

Requires:
- boto3
- Enviornment variables:
    - METRICS_SQS_QUEUE_URL: SQS queue URL for async metrics
    - ENVIRONMENT: Application environment (dev/staging/prod)

Usage:
    from aws_metrics import MetricsLogger
    
    # Initialize once per script run
    metrics = MetricsLogger(service_name="my-service")
    
    # Log events
    metrics.log_event("user_action", {"action": "login", "user_id": "123"})
    
    # Record metrics
    metrics.record_metric("response_time", 0.45)
    
    # Time operations
    with metrics.time_operation("database_query"):
        # your database code here
        pass
"""

import json
import time
import logging
import boto3
import threading
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Dict, Any, Union
from enum import Enum
import uuid
import os

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "Count"
    GAUGE = "None"
    TIMER = "Seconds"

class LogLevel(Enum):
    """Log levels"""
    INFO = "INFO"
    WARN = "WARN" 
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class MetricsLogger:
    """
    Hybrid metrics logger for AWS applications
    
    Features:
    - Structured JSON logging to CloudWatch Logs
    - Critical metrics to CloudWatch Metrics
    - Async detailed metrics to SQS
    - Context management for timing operations
    - Thread-safe operations
    """
    
    def __init__(self, 
                 service_name: str,
                 version: str = "1.0.0",
                 environment: str = None,
                 sqs_queue_url: str = None,
                 cloudwatch_namespace: str = None,
                 enable_async_metrics: bool = True,
                 enable_cloudwatch_metrics: bool = True):
        """
        Initialize the metrics logger
        
        Args:
            service_name: Name of your service/application
            version: Application version
            environment: Environment (dev/staging/prod) - auto-detected from env vars
            sqs_queue_url: SQS queue URL for async metrics
            cloudwatch_namespace: CloudWatch namespace for metrics
            enable_async_metrics: Enable SQS async metrics
            enable_cloudwatch_metrics: Enable CloudWatch metrics
        """
        
        self.service_name = service_name
        self.version = version
        self.environment = environment or os.environ.get('ENVIRONMENT', 'unknown')
        self.session_id = str(uuid.uuid4())[:8]
        
        # Configuration
        self.sqs_queue_url = sqs_queue_url or os.environ.get('METRICS_SQS_QUEUE_URL')
        self.cloudwatch_namespace = cloudwatch_namespace or f"{service_name}/Metrics"
        self.enable_async_metrics = enable_async_metrics
        self.enable_cloudwatch_metrics = enable_cloudwatch_metrics
        
        # AWS clients (lazy initialization)
        self._cloudwatch_client = None
        self._sqs_client = None
        
        # Setup structured logging
        self._setup_logging()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Metrics buffer for async processing
        self._metrics_buffer = []
        
        # Log startup
        self.log_event("metrics_logger_initialized", {
            "service": self.service_name,
            "version": self.version,
            "environment": self.environment,
            "session_id": self.session_id
        })
    
    @property
    def cloudwatch_client(self):
        """Lazy initialization of CloudWatch client"""
        if self._cloudwatch_client is None:
            self._cloudwatch_client = boto3.client('cloudwatch')
        return self._cloudwatch_client
    
    @property  
    def sqs_client(self):
        """Lazy initialization of SQS client"""
        if self._sqs_client is None:
            self._sqs_client = boto3.client('sqs')
        return self._sqs_client
    
    def _setup_logging(self):
        """Setup structured JSON logging"""
        self.logger = logging.getLogger(f"{self.service_name}.metrics")
        self.logger.setLevel(logging.INFO)
        
        # Only add handler if none exist (avoid duplicates)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            
            # JSON formatter for structured logs
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            
            self.logger.addHandler(handler)
            self.logger.propagate = False
    
    def log_event(self, 
                  event_type: str, 
                  data: Dict[str, Any] = None,
                  level: LogLevel = LogLevel.INFO,
                  include_in_async: bool = True):
        """
        Log a structured event to CloudWatch Logs
        
        Args:
            event_type: Type/name of the event
            data: Additional event data
            level: Log level
            include_in_async: Whether to include in async metrics
        """
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "service": self.service_name,
            "version": self.version,
            "environment": self.environment,
            "session_id": self.session_id,
            "event_type": event_type,
            "level": level.value,
            "data": data or {}
        }
        
        # Log to CloudWatch Logs (structured JSON)
        log_message = json.dumps(log_entry, default=str)
        
        if level == LogLevel.ERROR:
            self.logger.error(log_message)
        elif level == LogLevel.WARN:
            self.logger.warning(log_message)
        elif level == LogLevel.DEBUG:
            self.logger.debug(log_message)
        else:
            self.logger.info(log_message)
        
        # Add to async metrics buffer
        if include_in_async and self.enable_async_metrics:
            with self._lock:
                self._metrics_buffer.append({
                    "type": "event",
                    "timestamp": timestamp,
                    "event_type": event_type,
                    "data": data or {},
                    "level": level.value
                })
    
    def record_metric(self,
                     metric_name: str,
                     value: Union[int, float],
                     metric_type: MetricType = MetricType.GAUGE,
                     unit: str = None,
                     dimensions: Dict[str, str] = None,
                     send_to_cloudwatch: bool = True):
        """
        Record a metric value
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            metric_type: Type of metric (Counter, Gauge, Timer)
            unit: Metric unit (auto-detected from type if not provided)
            dimensions: Additional dimensions for the metric
            send_to_cloudwatch: Send to CloudWatch Metrics immediately
        """
        
        timestamp = datetime.now(timezone.utc)
        unit = unit or metric_type.value
        
        # Default dimensions
        default_dimensions = {
            "Service": self.service_name,
            "Environment": self.environment,
            "Version": self.version
        }
        
        if dimensions:
            default_dimensions.update(dimensions)
        
        # Log the metric event
        self.log_event("metric_recorded", {
            "metric_name": metric_name,
            "value": value,
            "type": metric_type.name,
            "unit": unit,
            "dimensions": default_dimensions
        }, include_in_async=False)  # Avoid double-logging
        
        # Send to CloudWatch Metrics
        if send_to_cloudwatch and self.enable_cloudwatch_metrics:
            self._send_cloudwatch_metric(metric_name, value, unit, default_dimensions, timestamp)
        
        # Add to async metrics buffer
        if self.enable_async_metrics:
            with self._lock:
                self._metrics_buffer.append({
                    "type": "metric",
                    "timestamp": timestamp.isoformat(),
                    "metric_name": metric_name,
                    "value": value,
                    "metric_type": metric_type.name,
                    "unit": unit,
                    "dimensions": default_dimensions
                })
    
    def _send_cloudwatch_metric(self, metric_name: str, value: float, unit: str, 
                              dimensions: Dict[str, str], timestamp: datetime):
        """Send metric to CloudWatch"""
        try:
            # Convert dimensions to CloudWatch format
            cw_dimensions = [{"Name": k, "Value": v} for k, v in dimensions.items()]
            
            self.cloudwatch_client.put_metric_data(
                Namespace=self.cloudwatch_namespace,
                MetricData=[{
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": unit,
                    "Timestamp": timestamp,
                    "Dimensions": cw_dimensions
                }]
            )
        except Exception as e:
            # Don't let metrics failures break the main application
            self.log_event("cloudwatch_metric_error", {
                "error": str(e),
                "metric_name": metric_name
            }, level=LogLevel.ERROR, include_in_async=False)
    
    @contextmanager
    def time_operation(self, 
                      operation_name: str, 
                      record_metric: bool = True,
                      dimensions: Dict[str, str] = None):
        """
        Context manager for timing operations
        
        Args:
            operation_name: Name of the operation being timed
            record_metric: Whether to record the timing as a CloudWatch metric
            dimensions: Additional dimensions for the timing metric
        
        Usage:
            with metrics.time_operation("database_query"):
                result = database.query(...)
        """
        
        start_time = time.time()
        
        # Log operation start
        self.log_event("operation_started", {
            "operation": operation_name,
            "start_time": datetime.now(timezone.utc).isoformat()
        })
        
        exception_occurred = False
        
        try:
            yield
            
        except Exception as e:
            exception_occurred = True
            duration = time.time() - start_time
            
            # Log operation failed
            self.log_event("operation_failed", {
                "operation": operation_name,
                "duration": duration,
                "error": str(e),
                "error_type": type(e).__name__
            }, level=LogLevel.ERROR)
            
            # Record failure metric
            if record_metric:
                failure_dimensions = {"Operation": operation_name, "Status": "Failed"}
                if dimensions:
                    failure_dimensions.update(dimensions)
                
                self.record_metric(
                    f"{operation_name}_duration",
                    duration,
                    MetricType.TIMER,
                    dimensions=failure_dimensions
                )
                
                self.record_metric(
                    "operation_failures",
                    1,
                    MetricType.COUNTER,
                    dimensions=failure_dimensions
                )
            
            raise  # Re-raise the exception
            
        finally:
            if not exception_occurred:
                duration = time.time() - start_time
                
                # Log operation completed
                self.log_event("operation_completed", {
                    "operation": operation_name,
                    "duration": duration,
                    "end_time": datetime.now(timezone.utc).isoformat()
                })
                
                # Record success metric
                if record_metric:
                    success_dimensions = {"Operation": operation_name, "Status": "Success"}
                    if dimensions:
                        success_dimensions.update(dimensions)
                    
                    self.record_metric(
                        f"{operation_name}_duration",
                        duration,
                        MetricType.TIMER,
                        dimensions=success_dimensions
                    )
                    
                    self.record_metric(
                        "operation_successes", 
                        1,
                        MetricType.COUNTER,
                        dimensions=success_dimensions
                    )
    
    def log_error(self, 
                  error: Exception, 
                  context: Dict[str, Any] = None,
                  operation: str = None):
        """
        Log an error with full context
        
        Args:
            error: The exception object
            context: Additional context about the error
            operation: Name of the operation where error occurred
        """
        
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "operation": operation,
            "context": context or {}
        }
        
        self.log_event("error_occurred", error_data, level=LogLevel.ERROR)
        
        # Record error metric
        self.record_metric(
            "errors_total",
            1,
            MetricType.COUNTER,
            dimensions={
                "ErrorType": type(error).__name__,
                "Operation": operation or "unknown"
            }
        )
    
    def flush_async_metrics(self):
        """
        Flush buffered metrics to SQS
        Call this at the end of your script or periodically
        """
        
        if not self.enable_async_metrics or not self.sqs_queue_url:
            return
        
        with self._lock:
            if not self._metrics_buffer:
                return
            
            # Prepare async metrics payload
            payload = {
                "service": self.service_name,
                "version": self.version,
                "environment": self.environment,
                "session_id": self.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metrics_count": len(self._metrics_buffer),
                "metrics": self._metrics_buffer.copy()
            }
            
            # Clear buffer
            self._metrics_buffer.clear()
        
        # Send to SQS
        try:
            self.sqs_client.send_message(
                QueueUrl=self.sqs_queue_url,
                MessageBody=json.dumps(payload, default=str)
            )
            
            self.log_event("async_metrics_sent", {
                "metrics_count": payload["metrics_count"],
                "queue_url": self.sqs_queue_url
            }, include_in_async=False)
            
        except Exception as e:
            self.log_event("async_metrics_error", {
                "error": str(e),
                "metrics_count": payload["metrics_count"]
            }, level=LogLevel.ERROR, include_in_async=False)
    
    def increment_counter(self, 
                         counter_name: str, 
                         value: int = 1,
                         dimensions: Dict[str, str] = None):
        """
        Convenience method to increment a counter
        
        Args:
            counter_name: Name of the counter
            value: Value to increment by (default: 1)
            dimensions: Additional dimensions
        """
        self.record_metric(counter_name, value, MetricType.COUNTER, dimensions=dimensions)
    
    def set_gauge(self, 
                  gauge_name: str, 
                  value: Union[int, float],
                  dimensions: Dict[str, str] = None):
        """
        Convenience method to set a gauge value
        
        Args:
            gauge_name: Name of the gauge
            value: Gauge value
            dimensions: Additional dimensions
        """
        self.record_metric(gauge_name, value, MetricType.GAUGE, dimensions=dimensions)
    
    def record_timing(self, 
                     timing_name: str, 
                     duration: float,
                     dimensions: Dict[str, str] = None):
        """
        Convenience method to record a timing
        
        Args:
            timing_name: Name of the timing metric
            duration: Duration in seconds
            dimensions: Additional dimensions
        """
        self.record_metric(timing_name, duration, MetricType.TIMER, dimensions=dimensions)
    
    def shutdown(self):
        """
        Shutdown the metrics logger
        Flushes any remaining async metrics
        """
        self.log_event("metrics_logger_shutdown", {
            "session_id": self.session_id,
            "buffered_metrics": len(self._metrics_buffer)
        })
        
        # Flush any remaining metrics
        self.flush_async_metrics()


# Convenience function for one-time setup
def create_metrics_logger(service_name: str, **kwargs) -> MetricsLogger:
    """
    Create a metrics logger instance
    
    Args:
        service_name: Name of your service
        **kwargs: Additional arguments for MetricsLogger
    
    Returns:
        Configured MetricsLogger instance
    """
    return MetricsLogger(service_name, **kwargs)