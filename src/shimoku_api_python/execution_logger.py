import logging
import os
from sys import stdout
from typing import Callable, Optional
from io import TextIOWrapper
from functools import wraps
from warnings import warn
from inspect import stack
import asyncio
import psutil
import time


# Got this code from https://code.activestate.com/recipes/412603-stack-based-indentation-of-formatted-logging/
class IndentFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.baseline = len(stack())

    def format(self, rec):
        _stack = stack()
        # we eliminate the unnecessary indents
        arrow = ('<- ' if 'Finished' in rec.msg else ('-> ' if 'Starting' in rec.msg else '| '))
        rec.indent = (' ' if rec.levelname == 'INFO' else '')+'｜ ' * (len(_stack) - self.baseline - 5) + arrow
        out = logging.Formatter.format(self, rec)
        del rec.indent
        return out


def my_before_sleep(retry_state):
    msg = f'Retrying {retry_state.fn}: attempt {retry_state.attempt_number} ended with: {retry_state.outcome}'
    logging.warning(msg)


def logging_before_and_after(logging_level: Callable, before: Optional[str] = None, after: Optional[str] = None) -> Callable:

    def decorator(func: Callable) -> Callable:

        #Async version
        @wraps(func)
        async def awrapper(*args, **kwargs):
            underlined_text = '\033[4m' + func.__name__ + '\033[0m'
            logging_level(f"Starting execution of function: {underlined_text}")
            initial_time = time.time()
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 ** 2
            if before:
                logging_level(before)

            result = await func(*args, **kwargs)

            if after:
                logging_level(after)

            time_spent = 1000*(time.time()-initial_time)
            memory_spent = ''
            if logging.root.isEnabledFor(logging.DEBUG):
                memory_spent = f', memory usage: {(process.memory_info().rss / 1024 ** 2) - initial_memory: .2f} MB'
            logging_level(
                f"Finished execution of function: {underlined_text}, "
                f"elapsed time: {time_spent:.2f} ms"
                f"{memory_spent}")

            return result

        #Normal version
        @wraps(func)
        def wrapper(*args, **kwargs):
            underlined_text = '\033[4m' + func.__name__ + '\033[0m'
            logging_level(f"Starting execution of function: {underlined_text}")
            initial_time = time.time()
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 ** 2
            if before:
                logging_level(before)

            result = func(*args, **kwargs)

            if after:
                logging_level(after)

            time_spent = 1000*(time.time()-initial_time)
            memory_spent = ''
            if logging.root.isEnabledFor(logging.DEBUG):
                memory_spent = f', memory usage: {(process.memory_info().rss / 1024 ** 2) - initial_memory: .2f} MB'
            logging_level(
                f"Finished execution of function: {underlined_text}, "
                f"elapsed time: {time_spent:.2f} ms"
                f"{memory_spent}")

            return result

        return wrapper if not asyncio.iscoroutinefunction(func) else awrapper

    return decorator


def configure_logging(verbosity: Optional[str] = None, channel: Optional[TextIOWrapper] = stdout):

    verbosity = verbosity.upper()
    if verbosity not in ['DEBUG', 'INFO', 'WARNING']:
        raise ValueError(f"Invalid value for verbosity, only 'DEBUG' and 'INFO' are permitted, "
                         f"the value provided is: {verbosity}")

    if not hasattr(channel, 'write'):
        warn("Specified channel doesn't have a 'write' method, using standard output", RuntimeWarning)
        channel = stdout

    _format = f'%(asctime)s | %(levelname)s {"| %(indent)s%(name)s " if verbosity == "DEBUG" else ""}| %(message)s'
    # create a formatter and set its format and date format
    formatter = logging.Formatter(_format, datefmt='%Y-%m-%d %H:%M') if verbosity != 'DEBUG' \
        else IndentFormatter(_format, datefmt='%Y-%m-%d %H:%M')

    level = logging.DEBUG if verbosity == 'DEBUG' else (logging.INFO if verbosity == 'INFO' else logging.WARNING)
    # change the root logger
    logging.basicConfig(
        stream=channel,
        datefmt='%Y-%m-%d %H:%M',
        format=_format,
        level=level
    )

    # change all the logger handlers
    logging.getLogger().setLevel(level)

    for handler in logging.root.handlers:
        handler.setFormatter(formatter)
        handler.stream = channel
