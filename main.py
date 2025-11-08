#!/usr/bin/env python3

import sys
from models import Queue
from services import decode_command


def main():
    """
    Main entry point for QueueCTL.
    Provides an interactive command-line interface for job queue management.
    """
    print("Welcome to QueueCTL")
    
    # Initialize the queue
    queue = Queue()
    handles = []
    
    try:
        while True:
            # Display prompt
            sys.stdout.write(">> ")
            sys.stdout.flush()
            
            # Read user input
            try:
                command = input()
            except EOFError:
                break
            
            # Check for exit command
            if command.strip() == "exit":
                break
            
            # Process the command
            result = decode_command(command.strip(), queue)
            
            if result is not None:
                handles = result
    
    except KeyboardInterrupt:
        print("\nReceived interrupt, shutting down...")
    
    finally:
        # Stop all worker threads
        if handles:
            print("Stopping all worker threads...")
            queue.stop = True
            
            # Wait for all threads to complete
            for handle in handles:
                handle.join()
            
            print("All worker threads stopped successfully")


if __name__ == "__main__":
    main()
