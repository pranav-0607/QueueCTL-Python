import json
from models import Jobs, Queue, State
from datetime import datetime


def decode_command(command, queue):
    """
    Decode and execute commands from user input.
    Returns list of thread handles if worker threads are started, None otherwise.
    """
    command = command.strip()
    
    if "enqueue" in command:
        # Extract JSON job data after "enqueue"
        job_str = command.split("enqueue", 1)[1].strip()
        print(f"Job is {job_str}")
        
        try:
            job_data = json.loads(job_str)
            max_retries = queue.max_retries
            
            job = Jobs(
                    id=queue.get_next_job_id(),                command=job_data["command"],
                                    command=job_data["command"] + " " + " ".join(job_data.get("args", [])),
                state=State.PENDING,
                attempts=0,
                max_retries=max_retries,
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )
            queue.enqueue(job)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format: {e}")
        except KeyError as e:
            print(f"Missing required field: {e}")
        
        return None
    
    elif "status" in command:
        # Get status of all jobs
        jobs = queue.all_jobs()
        print(f"All jobs are here {jobs}")
        return None
    
    elif "list --state" in command:
        # List jobs by state
        state = command.split("--state", 1)[1].strip()
        print(f"State is {state}")
        
        if state == "pending":
            pending_queues = queue.get_pending_or_failed_jobs(True, False)
            print(f"Pending queues are {pending_queues}")
        elif state == "processing":
            processing_queues = queue.get_pending_or_failed_jobs(False, True)
            print(f"Processing queues are {processing_queues}")
        elif state == "dead":
            dead_queues = queue.get_dead_letter_queue()
            print(f"Dead queues are {dead_queues}")
        elif state == "failed":
            failed_queues = queue.get_pending_or_failed_jobs(False, False)
            print(f"Failed queues are {failed_queues}")
        else:
            print("Invalid state, Enter a valid state")
        
        return None
    
    elif "dlq list" in command:
        # List dead letter queue
        print(f"Dead letter queue is {queue.get_dead_letter_queue()}")
        return None
    
    elif "dlq retry" in command:
        # Retry a job from dead letter queue
        job_id = command.split("retry", 1)[1].strip()
        print(f"Job id is {job_id}")
        queue.retry_dead_job(job_id)
        return None
    
    elif "set max-retries" in command:
        # Set max retries - extract number from command
        try:
            parts = command.split()
            if len(parts) >= 3:
                max_retries = int(parts[-1])
                queue.update_max_retries(max_retries)
                print(f"Max retries set to {max_retries}")
            else:
                queue.update_max_retries(10)
                print("Max retries set to 10 (default)")
        except ValueError:
            print("Invalid max-retries value")
        return None
    
    elif "worker start" in command:
        # Start worker threads
        # Extract number of threads if specified, default to 10
        try:
            parts = command.split()
            num_threads = 10
            if len(parts) >= 3:
                num_threads = int(parts[-1])
            handles = queue.start_threads(num_threads)
            print(f"Started {num_threads} worker threads")
            return handles
        except ValueError:
            handles = queue.start_threads(10)
            print("Started 10 worker threads (default)")
            return handles
    
    elif "worker stop" in command:
        # Stop all worker threads
        print("Stopping all the worker threads")
        queue.stop = True
        print("All the worker threads stopped")
        return None
    
    else:
        print("Invalid command, Enter a valid command")
        return None
