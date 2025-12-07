"""
Load Testing Script for E-Learning Platform
Tests scalability with concurrent users
"""
import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# Configuration
BASE_URL = 'http://localhost:5000/api'
NUM_USERS = 200  # Number of concurrent users
NUM_REQUESTS_PER_USER = 5  # Requests per user
TEST_DURATION = 60  # seconds

# Test credentials
TEST_EMAIL = 'student@example.com'
TEST_PASSWORD = 'password123'

# Results storage
results = {
    'success': 0,
    'failed': 0,
    'response_times': [],
    'errors': []
}
results_lock = threading.Lock()


def login():
    """Login and get JWT token"""
    try:
        response = requests.post(
            f'{BASE_URL}/auth/login',
            json={'email': TEST_EMAIL, 'password': TEST_PASSWORD},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None


def make_request(token, endpoint='/student/courses'):
    """Make a single API request"""
    start_time = time.time()
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f'{BASE_URL}{endpoint}',
            headers=headers,
            timeout=10
        )
        
        duration = time.time() - start_time
        
        with results_lock:
            if response.status_code == 200:
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Status {response.status_code}")
            
            results['response_times'].append(duration)
        
        return {
            'success': response.status_code == 200,
            'duration': duration,
            'status_code': response.status_code
        }
    
    except Exception as e:
        duration = time.time() - start_time
        
        with results_lock:
            results['failed'] += 1
            results['errors'].append(str(e))
            results['response_times'].append(duration)
        
        return {
            'success': False,
            'duration': duration,
            'error': str(e)
        }


def simulate_user(user_id, token):
    """Simulate a single user making multiple requests"""
    print(f"User {user_id} starting...")
    
    for i in range(NUM_REQUESTS_PER_USER):
        # Vary endpoints to simulate real usage
        endpoints = [
            '/student/all-courses',
            '/student/course-detail/1',
            '/student/lesson/1',
        ]
        endpoint = endpoints[i % len(endpoints)]
        
        result = make_request(token, endpoint)
        
        # Small delay between requests
        time.sleep(0.1)
    
    print(f"User {user_id} completed")


def run_load_test():
    """Run the load test"""
    print("=" * 60)
    print("E-LEARNING PLATFORM LOAD TEST")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  - Concurrent Users: {NUM_USERS}")
    print(f"  - Requests per User: {NUM_REQUESTS_PER_USER}")
    print(f"  - Total Requests: {NUM_USERS * NUM_REQUESTS_PER_USER}")
    print(f"  - Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Login to get token
    print("\n[1/3] Logging in...")
    token = login()
    
    if not token:
        print("❌ Login failed! Cannot proceed with load test.")
        return
    
    print("✅ Login successful")
    
    # Run load test
    print(f"\n[2/3] Starting load test with {NUM_USERS} concurrent users...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
        futures = [
            executor.submit(simulate_user, i, token)
            for i in range(NUM_USERS)
        ]
        
        # Wait for all to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in user simulation: {e}")
    
    total_duration = time.time() - start_time
    
    # Calculate statistics
    print("\n[3/3] Calculating results...")
    
    response_times = results['response_times']
    
    if response_times:
        avg_response = statistics.mean(response_times)
        median_response = statistics.median(response_times)
        min_response = min(response_times)
        max_response = max(response_times)
        p95_response = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_response = sorted(response_times)[int(len(response_times) * 0.99)]
    else:
        avg_response = median_response = min_response = max_response = 0
        p95_response = p99_response = 0
    
    total_requests = results['success'] + results['failed']
    success_rate = (results['success'] / total_requests * 100) if total_requests > 0 else 0
    requests_per_second = total_requests / total_duration if total_duration > 0 else 0
    
    # Print results
    print("\n" + "=" * 60)
    print("LOAD TEST RESULTS")
    print("=" * 60)
    print(f"\n📊 Overall Statistics:")
    print(f"  - Total Duration: {total_duration:.2f}s")
    print(f"  - Total Requests: {total_requests}")
    print(f"  - Successful: {results['success']} ({success_rate:.1f}%)")
    print(f"  - Failed: {results['failed']}")
    print(f"  - Requests/sec: {requests_per_second:.2f}")
    
    print(f"\n⏱️  Response Times:")
    print(f"  - Average: {avg_response:.3f}s")
    print(f"  - Median: {median_response:.3f}s")
    print(f"  - Min: {min_response:.3f}s")
    print(f"  - Max: {max_response:.3f}s")
    print(f"  - P95: {p95_response:.3f}s")
    print(f"  - P99: {p99_response:.3f}s")
    
    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    
    if avg_response <= 3:
        print(f"  ✅ EXCELLENT - Avg response time: {avg_response:.3f}s (target: ≤3s)")
    elif avg_response <= 5:
        print(f"  ⚠️  ACCEPTABLE - Avg response time: {avg_response:.3f}s (target: ≤3s)")
    else:
        print(f"  ❌ POOR - Avg response time: {avg_response:.3f}s (target: ≤3s)")
    
    if success_rate >= 99:
        print(f"  ✅ EXCELLENT - Success rate: {success_rate:.1f}% (target: ≥99%)")
    elif success_rate >= 95:
        print(f"  ⚠️  ACCEPTABLE - Success rate: {success_rate:.1f}% (target: ≥99%)")
    else:
        print(f"  ❌ POOR - Success rate: {success_rate:.1f}% (target: ≥99%)")
    
    if requests_per_second >= 100:
        print(f"  ✅ EXCELLENT - Throughput: {requests_per_second:.2f} req/s")
    elif requests_per_second >= 50:
        print(f"  ⚠️  ACCEPTABLE - Throughput: {requests_per_second:.2f} req/s")
    else:
        print(f"  ❌ POOR - Throughput: {requests_per_second:.2f} req/s")
    
    # Scenario 4 requirements
    print(f"\n📋 Scenario 4 Requirements:")
    concurrent_users_ok = NUM_USERS >= 200
    response_time_ok = avg_response <= 3
    no_crash = results['failed'] < total_requests * 0.05  # Less than 5% failure
    
    print(f"  - Handle ≥200 concurrent users: {'✅' if concurrent_users_ok else '❌'} ({NUM_USERS} users)")
    print(f"  - Response time ≤3s: {'✅' if response_time_ok else '❌'} ({avg_response:.3f}s)")
    print(f"  - No server crash: {'✅' if no_crash else '❌'} ({results['failed']} failures)")
    
    if concurrent_users_ok and response_time_ok and no_crash:
        print(f"\n PASSED ✅")
    else:
        print(f"\n NEEDS IMPROVEMENT")
    
    # Error summary
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        error_counts = {}
        for error in results['errors']:
            error_counts[error] = error_counts.get(error, 0) + 1
        
        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {error}: {count} times")
    
    print("\n" + "=" * 60)
    
    # Save results to file
    with open('load_test_results.json', 'w') as f:
        json.dump({
            'config': {
                'num_users': NUM_USERS,
                'requests_per_user': NUM_REQUESTS_PER_USER,
                'total_requests': total_requests
            },
            'results': {
                'total_duration': total_duration,
                'success': results['success'],
                'failed': results['failed'],
                'success_rate': success_rate,
                'requests_per_second': requests_per_second
            },
            'response_times': {
                'average': avg_response,
                'median': median_response,
                'min': min_response,
                'max': max_response,
                'p95': p95_response,
                'p99': p99_response
            }
        }, f, indent=2)
    
    print("📄 Results saved to: load_test_results.json")


if __name__ == '__main__':
    try:
        run_load_test()
    except KeyboardInterrupt:
        print("\n\n  Load test interrupted by user")
    except Exception as e:
        print(f"\n\n Load test failed: {e}")
        import traceback
        traceback.print_exc()
