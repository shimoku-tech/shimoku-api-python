import logging
from sys import stdout
from typing import Callable, Optional
from functools import wraps


def configure_logging(verbose: Optional[str] = None):
    logging.basicConfig(
        stream=stdout,
        datefmt='%Y-%m-%d %H:%M',
        format=f'%(asctime)s | %(levelname)s {"| %(name)s" if verbose == "DEBUG" else ""}| %(message)s',
        level=logging.DEBUG if verbose == 'DEBUG' else (logging.INFO if verbose == 'INFO' else logging.WARNING)
    )


def logging_before_and_after(logging_level: Callable, before: Optional[str] = None, after: Optional[str] = None):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging_level("Starting execution of function: %s", func.__name__)
            if before:
                logging_level(before)
            result = func(*args, **kwargs)
            if after:
                logging_level(after)
            logging_level("Finished execution of function: %s", func.__name__)
            return result

        return wrapper

    return decorator
