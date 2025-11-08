# QueueCTL-Python

Python port of QueueCTL - A command-line tool to run commands concurrently with shared state management and job queue functionality.

## Overview

QueueCTL-Python is a job queue management system that allows you to:
- Enqueue jobs with shell commands
- Track job states (Pending, Processing, Completed, Failed, Dead)
- Manage worker threads for concurrent job execution
- Handle retries and dead letter queue (DLQ)
- Monitor job status in real-time

## Requirements

- Python 3.7 or higher
- All dependencies are from Python standard library (no external packages required)

## Installation

```bash
# Clone the repository
git clone https://github.com/pranav-0607/QueueCTL-Python.git
cd QueueCTL-Python

# Run the application
python main.py
```

## Usage

Start the QueueCTL interactive shell:

```bash
python main.py
```

### Commands

#### 1. Enqueue a Job

Add a new job to the queue with a shell command:

```
enqueue {"command": "echo Hello World", "args": []}
```

Example with arguments:
```
enqueue {"command": "python", "args": ["-c", "print('Hello from Python')"]}
```

#### 2. View Job Status

Display all jobs and their current states:

```
status
```

#### 3. List Jobs by State

Filter jobs by their current state:

```
list --state pending
list --state processing
list --state completed
list --state failed
list --state dead
```

#### 4. Worker Management

Start worker threads to process jobs:

```
worker start 3
```

Stop all worker threads:

```
worker stop
```

#### 5. Set Maximum Retries

Configure the maximum number of retry attempts for failed jobs:

```
set max-retries 5
```

#### 6. Dead Letter Queue (DLQ) Commands

List all jobs in the dead letter queue:

```
dlq list
```

Retry a specific job from the DLQ:

```
dlq retry <job_id>
```

#### 7. Exit

Exit the QueueCTL shell:

```
exit
```

Or press `Ctrl+C`

## Architecture

### Files

- **main.py** - Entry point with interactive CLI loop
- **models.py** - Core data structures (Queue, Jobs, State enum)
- **services.py** - Command decoder and execution logic
- **requirements.txt** - Documentation of Python standard library modules used

### Job States

1. **PENDING** - Job has been enqueued, waiting to be processed
2. **PROCESSING** - Job is currently being executed by a worker
3. **COMPLETED** - Job finished successfully (exit code 0)
4. **FAILED** - Job failed but can be retried
5. **DEAD** - Job exceeded max retries and moved to dead letter queue

### Thread Safety

The Queue uses Python's `threading.Lock` to ensure thread-safe operations when multiple workers access shared state concurrently.

## Examples

### Basic Workflow

```
# Start QueueCTL
python main.py

# Enqueue some jobs
enqueue {"command": "echo", "args": ["Task 1"]}
enqueue {"command": "echo", "args": ["Task 2"]}
enqueue {"command": "sleep", "args": ["2"]}

# Start workers
worker start 2

# Check status
status

# List pending jobs
list --state pending

# Stop workers when done
worker stop

# Exit
exit
```

### Handling Failures

```
# Enqueue a job that will fail
enqueue {"command": "false", "args": []}

# Set max retries
set max-retries 3

# Start worker
worker start 1

# Check failed jobs
list --state failed

# Check dead letter queue
dlq list

# Retry a dead job
dlq retry 1
```

## Differences from Rust Version

- Uses Python's `threading` module instead of Rust's thread handling
- Uses `subprocess` module for command execution instead of Rust's `Command`
- Uses `threading.Lock` instead of Rust's `Arc<RwLock>`
- Uses `collections.deque` instead of Rust's `VecDeque`
- Maintains identical functionality and command interface

## License

This project is a Python port of the original QueueCTL written in Rust.

## Contributing

Feel free to open issues or submit pull requests for improvements!
