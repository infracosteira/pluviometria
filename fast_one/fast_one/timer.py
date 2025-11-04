import time
import logging


class Timer:
    """
    A simple context manager to measure the execution time of a code block and log the result.

    If a logger is not provided, it will fall back to using print().
    
    Example:
        with Timer("Processing data", logger=logger):
            # your code here
    """
    def __init__(self, description="Block of code", logger=None, level=logging.INFO):
        self.description = description
        self.logger = logger
        self.level = level
        self.start_time = None

    def __enter__(self):
        """Called when entering the 'with' block."""
        pass
        """ self.start_time = time.perf_counter()
        message = f"\nStarting '{self.description}'..."
        
        if self.logger:
            self.logger.log(self.level, message)
        else:
            print(message)
        
        return self """

    def __exit__(self, exc_type, exc_value, traceback):
        """Called when exiting the 'with' block."""

        pass

        """ end_time = time.perf_counter()
        duration = end_time - self.start_time
        
        message = f"\n'{self.description}' finished in {duration:.4f} seconds."
        
        if self.logger:
            self.logger.log(self.level, message)
        else:
            print(message)
        """