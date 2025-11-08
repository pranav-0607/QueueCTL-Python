from enum import Enum
from collections import deque
from threading import Lock, Thread
import subprocess
from datetime import datetime


class State(Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    DEAD = "Dead"


class Jobs:
    def __init__(self, id, command, state, attempts, max_retries, created_at, updated_at):
        self.id = id
        self.command = command
        self.state = state
        self.attempts = attempts
        self.max_retries = max_retries
        self.created_at = created_at
        self.updated_at = updated_at

    def clone(self):
        return Jobs(
            self.id,
            self.command,
            self.state,
            self.attempts,
            self.max_retries,
            self.created_at,
            self.updated_at
        )

    def __repr__(self):
        return f"Jobs(id={self.id}, command={self.command}, state={self.state}, attempts={self.attempts})"


class Queue:
    def __init__(self):
        self.jobs = deque()
        self.dead_letter_queue = deque()
        self.completed_jobs = deque()
        self.max_retries = 3
        self.stop = False
        self.lock = Lock()
                self.next_job_id = 1

    def update_max_retries(self, max_retries):
        self.max_retries = max_retries

        def get_next_job_id(self):
        with self.lock:
            job_id = self.next_job_id
            self.next_job_id += 1
            return job_id

    def enqueue(self, job):
        with self.lock:
            self.jobs.append(job)
            print("Job enqueued successfully")

    def start_threads(self, no_of_threads):
        list_worker_threads = []
        for x in range(no_of_threads):
            thread = Thread(target=self._worker)
            thread.start()
            list_worker_threads.append(thread)
        return list_worker_threads

    def _worker(self):
        while not self.stop:
            front_value = None
            with self.lock:
                if len(self.jobs) > 0:
                    front_value = self.jobs.popleft()

            if front_value:
                try:
                    result = subprocess.run(
                        front_value.command.strip(),
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    output = result.stdout
                    print(f"Output: {output} and length of the output was {len(output)}")

                    if "failed" in output.lower() or "error" in output.lower() or "not exists" in output.lower() or result.returncode != 0:
                        value = front_value.clone()
                        if value.attempts >= value.max_retries:
                            value.state = State.DEAD
                            value.updated_at = datetime.utcnow().isoformat()
                            with self.lock:
                                self.dead_letter_queue.append(value)
                        else:
                            value.state = State.FAILED
                            value.updated_at = datetime.utcnow().isoformat()
                            value.attempts += 1
                            with self.lock:
                                self.jobs.append(value)
                        print(f"{front_value.command} job failed")
                    else:
                        value = front_value.clone()
                        value.state = State.COMPLETED
                        value.updated_at = datetime.utcnow().isoformat()
                        with self.lock:
                            self.completed_jobs.append(value)
                except Exception as e:
                    print(f"Error executing command: {e}")
                    value = front_value.clone()
                    value.state = State.FAILED
                    value.updated_at = datetime.utcnow().isoformat()
                    value.attempts += 1
                    if value.attempts >= value.max_retries:
                        value.state = State.DEAD
                        with self.lock:
                            self.dead_letter_queue.append(value)
                    else:
                        with self.lock:
                            self.jobs.append(value)

    def get_dead_letter_queue(self):
        with self.lock:
            return list(self.dead_letter_queue)

    def get_pending_or_failed_jobs(self, pending, processing):
        jobs_list = []
        with self.lock:
            for value in self.jobs:
                if pending and value.state == State.PENDING:
                    jobs_list.append(value)
                elif processing and value.state == State.PROCESSING:
                    jobs_list.append(value)
                elif not pending and not processing and value.state == State.FAILED:
                    jobs_list.append(value)
        return jobs_list

    def retry_dead_job(self, job_id):
        with self.lock:
            for index, value in enumerate(self.dead_letter_queue):
                if value.id == job_id:
                    value = value.clone()
                    value.state = State.PENDING
                    value.attempts = 0
                    value.updated_at = datetime.utcnow().isoformat()
                    self.jobs.append(value)
                    del self.dead_letter_queue[index]
                    return

    def all_jobs(self):
        print("Includes all state jobs")
        with self.lock:
            jobs_list = list(self.jobs) + list(self.dead_letter_queue) + list(self.completed_jobs)
        return jobs_list
