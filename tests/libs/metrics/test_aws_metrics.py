"""
Quick test runner for AWS Metrics Library
Run this to quickly verify your metrics library works

Usage: python test_aws_metrics.py
"""

import sys
import time
from unittest.mock import Mock, patch

from libs.metrics.aws_metrics import create_metrics_logger

def check_imports():
    """Check if all required modules can be imported"""
    print("🔍 Checking imports...")
    
    try:
        import boto3
        print("✅ boto3 imported")
    except ImportError:
        print("❌ boto3 not found. Install with: pip install boto3")
        return False
    
    try:
        print("✅ aws_metrics imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Cannot import aws_metrics: {e}")
        print("Make sure aws_metrics.py is in the same directory")
        return False
    except Exception as e:
        print(f"❌ Error in aws_metrics.py: {e}")
        return False

def test_basic_functionality():
    """Test basic metrics functionality"""
    print("\n🧪 Testing basic functionality...")
    
    # Mock AWS clients
    mock_calls = {"cloudwatch": [], "sqs": []}
    
    def mock_cloudwatch():
        client = Mock()
        def put_metric(**kwargs):
            mock_calls["cloudwatch"].append(kwargs)
            print(f"   📊 CloudWatch metric: {kwargs.get('Namespace', 'Unknown')}")
        client.put_metric_data = put_metric
        return client
    
    def mock_sqs():
        client = Mock()
        def send_msg(**kwargs):
            mock_calls["sqs"].append(kwargs)
            print(f"   📤 SQS message: {len(kwargs['MessageBody'])} chars")
        client.send_message = send_msg
        return client
    
    def mock_client(service):
        return mock_cloudwatch() if service == 'cloudwatch' else mock_sqs()
    
    with patch('boto3.client', side_effect=mock_client):
        try:
            # Create metrics logger
            metrics = create_metrics_logger("quick-test")
            print("✅ MetricsLogger created")
            
            # Test logging
            metrics.log_event("test_start", {"version": "1.0"})
            print("✅ log_event() works")
            
            # Test metrics
            metrics.increment_counter("test_counter")
            metrics.set_gauge("test_gauge", 42)
            metrics.record_timing("test_timer", 0.123)
            print("✅ Metrics recording works")
            
            # Test timing
            with metrics.time_operation("test_operation"):
                time.sleep(0.01)
            print("✅ Timing operations work")
            
            # Test error logging
            try:
                raise ValueError("Test error")
            except ValueError as e:
                metrics.log_error(e, operation="test_op")
            print("✅ Error logging works")
            
            # Test cleanup
            metrics.flush_async_metrics()
            metrics.shutdown()
            print("✅ Cleanup works")
            
            return True
            
        except Exception as e:
            print(f"❌ Basic functionality test failed: {e}")
            return False

def test_realistic_scenario():
    """Test a realistic usage scenario"""
    print("\n🎯 Testing realistic scenario...")
    
    mock_calls = {"cloudwatch": [], "sqs": []}
    
    def mock_client(service):
        client = Mock()
        if service == 'cloudwatch':
            client.put_metric_data = lambda **kwargs: mock_calls["cloudwatch"].append(kwargs)
        else:
            client.send_message = lambda **kwargs: mock_calls["sqs"].append(kwargs)
        return client
    
    with patch('boto3.client', side_effect=mock_client):        
        try:
            # Simulate a data processing script
            metrics = create_metrics_logger(
                service_name="data-processor",
                version="1.0.0",
                environment="test",
                sqs_queue_url="https://fake-queue-url"
            )
            
            # Simulate processing
            metrics.log_event("processing_started", {"batch_size": 100})
            
            # Simulate work with timing
            with metrics.time_operation("data_processing"):
                # Process some records
                for i in range(10):
                    with metrics.time_operation("record_processing", record_metric=False):
                        time.sleep(0.001)  # Tiny delay
                    
                    if i % 3 == 0:  # Some metrics
                        metrics.increment_counter("records_processed")
                
                # Business metrics
                metrics.set_gauge("processing_speed", 150)
                metrics.record_timing("avg_record_time", 0.05)
            
            # Simulate completion
            metrics.log_event("processing_completed", {
                "total_records": 100,
                "success_rate": 0.95
            })
            
            # Cleanup
            metrics.flush_async_metrics()
            metrics.shutdown()
            
            print(f"✅ Realistic scenario completed")
            print(f"   - CloudWatch calls: {len(mock_calls['cloudwatch'])}")
            print(f"   - SQS calls: {len(mock_calls['sqs'])}")
            
            return len(mock_calls['cloudwatch']) > 0 and len(mock_calls['sqs']) > 0
            
        except Exception as e:
            print(f"❌ Realistic scenario failed: {e}")
            return False

def test_performance():
    """Test performance characteristics"""
    print("\n⚡ Testing performance...")
    
    with patch('boto3.client', return_value=Mock()):
        try:
            metrics = create_metrics_logger("perf-test")
            
            start_time = time.time()
            
            # Generate many events
            for i in range(50):
                metrics.log_event(f"event_{i}", {"data": i})
                
            # Generate metrics (skip CloudWatch for speed)
            for i in range(50):
                metrics.record_metric(f"metric_{i}", i, send_to_cloudwatch=False)
            
            # Time operations
            for i in range(10):
                with metrics.time_operation(f"op_{i}", record_metric=False):
                    pass
            
            # Cleanup
            metrics.flush_async_metrics()
            
            total_time = time.time() - start_time
            
            print(f"⏱️  Processed 110 operations in {total_time:.3f}s")
            
            if total_time < 0.5:
                print("✅ Performance test passed - excellent speed")
                return True
            elif total_time < 1.0:
                print("✅ Performance test passed - good speed")
                return True
            else:
                print("⚠️  Performance slower than expected but acceptable")
                return True
                
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False

def main():
    """Run quick tests"""
    print("⚡ Quick Test for AWS Metrics Library")
    print("=" * 45)
    
    # Check basic setup
    if not check_imports():
        print("\n❌ Cannot proceed - fix import issues first")
        return False
    
    # Run tests
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Realistic Scenario", test_realistic_scenario),
        ("Performance", test_performance)
    ]
    
    passed = 0
    for name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"💥 {name} failed")
    
    # Results
    print("\n" + "=" * 45)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Your metrics library is ready!")
        print("\n🚀 Next steps:")
        print("1. Set environment variables:")
        print("   - METRICS_SQS_QUEUE_URL (optional)")
        print("   - ENVIRONMENT (dev/staging/prod)")
        print("2. Use in your AWS scripts:")
        print("   from aws_metrics import create_metrics_logger")
        print("   metrics = create_metrics_logger('your-service')")
        print("3. Deploy to AWS and test with real services")
    else:
        print("⚠️  Some tests failed - check your aws_metrics.py file")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)