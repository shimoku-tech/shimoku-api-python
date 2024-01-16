import logging
from sys import stdout
from typing import Callable, Optional
from io import TextIOWrapper
from functools import wraps
from inspect import stack
import asyncio
from time import perf_counter

logger = logging.getLogger(__name__)


# Got this code from https://code.activestate.com/recipes/412603-stack-based-indentation-of-formatted-logging/
class IndentFormatter(logging.Formatter):
    """ Formatter that adds indentation to logging messages based on the stack. """
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.baseline = len(stack())

    def format(self, rec):
        """ Format the specified record as text. """
        _stack = stack()
        # we eliminate the unnecessary indents
        arrow = ('<- ' if 'Finished' in rec.msg else ('-> ' if 'Starting' in rec.msg else '| '))
        rec.indent = (' ' if rec.levelname == 'INFO' else '')+'｜ ' * (len(_stack) - self.baseline - 5) + arrow
        out = logging.Formatter.format(self, rec)
        del rec.indent
        return out


def my_before_sleep(retry_state):
    """ Logging function called before sleeping between retries. """
    msg = f'Retrying {retry_state.fn}: attempt {retry_state.attempt_number} ended with: {retry_state.outcome}'
    logging.warning(msg)


def log_error(logger, message, errorFunction):
    """ Log an error and raise an exception. """
    logger.error(message)
    raise errorFunction(message)


def logging_before_and_after(logging_level: Callable) -> Callable:
    """ Decorator that logs before and after the execution of a function. """

    def decorator(func: Callable) -> Callable:

        def before_call(*args, **kwargs):
            """ Logs before the execution of the function. """
            enabled_for_debug = logging.root.isEnabledFor(logging.DEBUG)
            func_name = (func.__name__ if not enabled_for_debug else func.__qualname__)
            if 'logging_func_name' in kwargs:
                func_name = kwargs.pop('logging_func_name')

            underlined_text = '\033[4m' + func_name + '\033[0m'
            logging_level(
                f"Starting execution: {underlined_text}" +
                (f" with args: {args}, kwargs: {kwargs}" if enabled_for_debug else '')
            )
            initial_time = perf_counter()
            return initial_time, underlined_text

        def after_call(initial_time, underlined_text):
            """ Logs after the execution of the function. """
            time_spent = 1000*(perf_counter()-initial_time)
            memory_spent = ''
            logging_level(
                f"Finished execution: {underlined_text}, "
                f"elapsed time: {time_spent:.2f} ms"
                f"{memory_spent}")

        @wraps(func)
        async def awrapper(*args, **kwargs):
            """ Async version of the wrapper. """
            initial_time, underlined_text = before_call(*args, **kwargs)
            if 'logging_func_name' in kwargs:
                kwargs.pop('logging_func_name')
            result = await func(*args, **kwargs)
            after_call(initial_time, underlined_text)
            return result

        @wraps(func)
        def wrapper(*args, **kwargs):
            """ Normal version of the wrapper. """
            initial_time, underlined_text = before_call(*args, **kwargs)
            if 'logging_func_name' in kwargs:
                kwargs.pop('logging_func_name')
            result = func(*args, **kwargs)
            after_call(initial_time, underlined_text)
            return result

        return wrapper if not asyncio.iscoroutinefunction(func) else awrapper

    return decorator


def configure_logging(verbosity: Optional[str] = None, channel: Optional[TextIOWrapper] = stdout):
    """ Configures the logging module to use the specified verbosity and channel.
    :param verbosity: The verbosity level to use, can be 'DEBUG', 'INFO' or 'WARNING'.
    :param channel: The channel to use, can be a file or a stream.
    """

    verbosity = verbosity.upper()
    if verbosity not in ['DEBUG', 'INFO', 'WARNING']:
        raise ValueError(f"Invalid value for verbosity, only 'DEBUG' and 'INFO' are permitted, "
                         f"the value provided is: {verbosity}")

    if not hasattr(channel, 'write'):
        logger.warning("Specified channel doesn't have a 'write' method, using standard output")
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
