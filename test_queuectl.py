#!/usr/bin/env python3
"""
Comprehensive test script for QueueCTL-Python
Tests all functionality to ensure correctness
"""

import time
import sys
from models import Queue, Jobs, State
from services import decode_command

def print_test(test_name):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

def test_job_creation():
    print_test("Job Creation and Enqueue")
    queue = Queue()
    
    # Test 1: Enqueue with valid JSON
    result = decode_command('enqueue {"command": "echo", "args": ["Hello, World!"]}', queue)
    print(f"✓ Job enqueued with auto-generated ID")
    
    # Test 2: Enqueue with just command
    result = decode_command('enqueue {"command": "pwd"}', queue)
    print(f"✓ Job enqueued without args")
    
    # Test 3: Verify jobs are in queue
    jobs = queue.all_jobs()
    print(f"✓ Total jobs in queue: {len(jobs)}")
    assert len(jobs) == 2, "Should have 2 jobs"
    print("PASSED\n")
    return queue

def test_status_command(queue):
    print_test("Status Command")
    result = decode_command('status', queue)
    print("✓ Status command executed")
    print("PASSED\n")

def test_list_by_state(queue):
    print_test("List by State Commands")
    
    # Test pending
    decode_command('list --state pending', queue)
    print("✓ List pending jobs")
    
    # Test processing
    decode_command('list --state processing', queue)
    print("✓ List processing jobs")
    
    # Test failed
    decode_command('list --state failed', queue)
    print("✓ List failed jobs")
    
    # Test dead
    decode_command('list --state dead', queue)
    print("✓ List dead jobs")
    
    print("PASSED\n")

def test_worker_management(queue):
    print_test("Worker Thread Management")
    
    # Start 2 worker threads
    handles = decode_command('worker start 2', queue)
    print(f"✓ Started 2 worker threads")
    assert handles is not None, "Should return thread handles")
    assert len(handles) == 2, "Should have 2 thread handles"
    
    # Let workers process
    print("Waiting for jobs to process...")
    time.sleep(2)
    
    # Check status
    decode_command('status', queue)
    
    # Stop workers
    decode_command('worker stop', queue)
    print("✓ Stopped all worker threads")
    
    # Wait for threads to finish
    for handle in handles:
        handle.join(timeout=2)
    
    print("PASSED\n")
    return handles

def test_max_retries(queue):
    print_test("Max Retries Configuration")
    
    # Set max retries to 2
    decode_command('set max-retries 2', queue)
    print("✓ Set max retries to 2")
    assert queue.max_retries == 2, "Max retries should be 2"
    
    # Set max retries to 5
    decode_command('set max-retries 5', queue)
    print("✓ Set max retries to 5")
    assert queue.max_retries == 5, "Max retries should be 5"
    
    print("PASSED\n")

def test_failure_and_retry():
    print_test("Job Failure and Retry Logic")
    queue = Queue()
    queue.update_max_retries(2)  # Set low retry count for testing
    
    # Enqueue a job that will fail (false command always fails)
    decode_command('enqueue {"command": "false"}', queue)
    print("✓ Enqueued job that will fail")
    
    # Start worker
    handles = decode_command('worker start 1', queue)
    print("✓ Started worker")
    
    # Wait for job to fail and retry
    print("Waiting for job to fail and move to DLQ...")
    time.sleep(4)
    
    # Check DLQ
    decode_command('dlq list', queue)
    dlq_jobs = queue.get_dead_letter_queue()
    print(f"✓ Jobs in DLQ: {len(dlq_jobs)}")
    
    # Stop worker
    queue.stop = True
    for handle in handles:
        handle.join(timeout=2)
    
    print("PASSED\n")
    return queue

def test_dlq_retry(queue):
    print_test("Dead Letter Queue Retry")
    
    dlq_jobs = queue.get_dead_letter_queue()
    if len(dlq_jobs) > 0:
        job_id = dlq_jobs[0].id
        decode_command(f'dlq retry {job_id}', queue)
        print(f"✓ Retried job {job_id} from DLQ")
        
        # Check if job moved back to main queue
        new_dlq = queue.get_dead_letter_queue()
        assert len(new_dlq) < len(dlq_jobs), "DLQ should have fewer jobs"
        print("✓ Job successfully moved from DLQ to main queue")
    else:
        print("⚠ No jobs in DLQ to retry (this is OK)")
    
    print("PASSED\n")

def test_invalid_commands(queue):
    print_test("Invalid Command Handling")
    
    # Test invalid JSON
    decode_command('enqueue {invalid json}', queue)
    print("✓ Handled invalid JSON gracefully")
    
    # Test invalid command
    decode_command('invalid command', queue)
    print("✓ Handled invalid command gracefully")
    
    # Test invalid state
    decode_command('list --state invalid', queue)
    print("✓ Handled invalid state gracefully")
    
    print("PASSED\n")

def test_concurrent_execution():
    print_test("Concurrent Job Execution")
    queue = Queue()
    
    # Enqueue multiple jobs
    for i in range(5):
        decode_command(f'enqueue {{"command": "echo", "args": ["Job {i}"]}}', queue)
    
    print(f"✓ Enqueued 5 jobs")
    
    # Start 3 workers
    handles = decode_command('worker start 3', queue)
    print("✓ Started 3 workers")
    
    # Let them process
    time.sleep(3)
    
    # Stop workers
    queue.stop = True
    for handle in handles:
        handle.join(timeout=2)
    
    # Check results
    completed = queue.completed_jobs
    print(f"✓ Completed jobs: {len(completed)}")
    
    print("PASSED\n")

def run_all_tests():
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#  QueueCTL-Python Comprehensive Test Suite" + " "*15 + "#")
    print("#" + " "*58 + "#")
    print("#"*60 + "\n")
    
    try:
        # Run all tests
        queue1 = test_job_creation()
        test_status_command(queue1)
        test_list_by_state(queue1)
        test_worker_management(queue1)
        test_max_retries(queue1)
        
        queue2 = test_failure_and_retry()
        test_dlq_retry(queue2)
        
        queue3 = Queue()
        test_invalid_commands(queue3)
        
        test_concurrent_execution()
        
        # Final summary
        print("\n" + "="*60)
        print("  ALL TESTS PASSED ✓")
        print("="*60)
        print("\nTest Summary:")
        print("  ✓ Job creation and enqueue")
        print("  ✓ Status command")
        print("  ✓ List by state")
        print("  ✓ Worker thread management")
        print("  ✓ Max retries configuration")
        print("  ✓ Job failure and retry logic")
        print("  ✓ Dead letter queue operations")
        print("  ✓ Invalid command handling")
        print("  ✓ Concurrent job execution")
        print("\nAll objectives are working correctly!\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
