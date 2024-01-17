import asyncio

import json
from functools import wraps
from typing import Optional, Callable, Coroutine, Dict
import logging
from IPython.lib import backgroundjobs as bg
import time
from shimoku_api_python.execution_logger import logging_before_and_after, log_error

from copy import copy
logger = logging.getLogger(__name__)


class ExecutionPoolContext:
    """
    This class stores the arguments needed to execute the tasks in the task pool
    """

    def __init__(self, api_client):
        self.api_client = api_client
        self.ending_tasks: Dict[str, Coroutine] = {}
        self.task_pool = []
        self.free_context = {}
        # By default, set to true, to make the user aware that it is using the async configuration
        # (they will have to explicitly state it in their code)
        self.sequential = True
        self.universe = None

    def clear(self):
        self.ending_tasks = {}
        self.task_pool = []
        self.free_context = {}


def decorate_external_function(self, external_class, function_name) -> Callable:
    """
    This function is used to decorate a function from another class, getting all the context necessary from the self
    argument of the class where it is being called. This is done so that the execution_pool_context is only used by the
    user-access classes, and not by the low level SDK classes.
    """
    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.debug)
    async def call_function_from_class(self, external_class, function_name, *args, **kwargs):
        return await getattr(external_class, function_name)(*args, **kwargs)

    @wraps(getattr(external_class, function_name))
    def wrapper(*args, **kwargs):
        return call_function_from_class(self, external_class, function_name, *args, **kwargs)

    return wrapper


def async_auto_call_manager(execute: Optional[bool] = False) -> Callable:
    """
    Example:
        @async_auto_call_manager(execute=True)
        async def my_function():
            pass

    Decorator to manage the async execution of the tasks in the task pool, it's used to avoid making the user manage
    the async behavior of the functions, the syntax when calling the function is the same as the normal one, but it
    will be executed asynchronously when executing the task pool.

    :params execute: If True, the function will be executed immediately, otherwise it will be added to the task pool
    """

    def decorator(async_func: Callable) -> Callable:

        async def execute_ending_tasks(epc: ExecutionPoolContext):
            epc.task_pool.clear()
            if epc.ending_tasks:
                ending_tasks = copy(epc.ending_tasks)
                epc.ending_tasks.clear()
                await asyncio.gather(*ending_tasks.values())
                epc.ending_tasks = {}

        async def execute_tasks(epc: ExecutionPoolContext):
            # IMPORTANT!! Nothing has to be dependent on this code as the sequential execution needs to keep working
            epc.api_client.semaphore = asyncio.Semaphore(epc.api_client.semaphore_limit)

            # if just one task it's the same as sequential
            if len(epc.task_pool) == 1:
                task = epc.task_pool[0]
                epc.task_pool.clear()
                result = await task
                await execute_ending_tasks(epc)
                epc.free_context = {}
                return result

            task_pool = copy(epc.task_pool)
            epc.task_pool.clear()
            await asyncio.gather(*task_pool)
            await execute_ending_tasks(epc)
            epc.free_context = {}

        #TODO unify this two functions
        async def sequential_task_execution(epc: ExecutionPoolContext, coroutine: Coroutine):
            epc.api_client.semaphore = asyncio.Semaphore(epc.api_client.semaphore_limit)
            result = await coroutine
            await execute_ending_tasks(epc)
            epc.free_context = {}
            return result

        @wraps(async_func)
        def wrapper(self, *args, **kwargs):
            # Get the epc from the self argument, it's always the first element of the args
            epc: Optional[ExecutionPoolContext] = None
            if hasattr(self, 'epc'):
                epc: ExecutionPoolContext = self.epc
            else:
                log_error(logger, 'The async_auto_call_manager decorator can only be used in classes that '
                                  'have an epc attribute', RuntimeError)

            if epc.sequential or execute:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    # We are in a jupyter notebook, so we need to execute in a different loop
                    jobs = bg.BackgroundJobManager()
                    if len(epc.task_pool) > 0:
                        logger.info('Executing task pool')
                        job = jobs.new(asyncio.run, execute_tasks(epc))
                        while not job.finished and job.finished is not None:
                            time.sleep(0.1)

                    job = jobs.new(asyncio.run, sequential_task_execution(epc, async_func(self, *args, **kwargs)))
                    while not job.finished and job.finished is not None:
                        time.sleep(0.1)

                    if job.finished is None:
                        epc.universe.clear()
                        epc.clear()
                        log_error(logger, 'The execution of the task pool has been interrupted', RuntimeError)

                    return job.result
                else:
                    if len(epc.task_pool) > 0:
                        logger.info('Executing task pool')
                        asyncio.run(execute_tasks(epc))
                    return asyncio.run(sequential_task_execution(epc, async_func(self, *args, **kwargs)))

            check_before_async_execution: Optional[Callable] = getattr(self, 'check_before_async_execution', None)
            if callable(check_before_async_execution):
                check_before_async_execution(async_func, *args, **kwargs)

            _self = copy(self)  # copy the self object to avoid modifying the shallow data
            epc.task_pool.append(async_func(_self, *args, **kwargs))
            func_name = async_func.__name__
            if 'logging_func_name' in kwargs:
                func_name = kwargs['logging_func_name']

            logger.info(f'{func_name} added to the task pool')

        return wrapper

    return decorator
