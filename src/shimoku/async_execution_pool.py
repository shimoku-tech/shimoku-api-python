import asyncio
from abc import ABC
from typing import Optional, Callable, Dict, Union, Coroutine, Any, Type
import logging
from shimoku import nest_asyncio
from shimoku.utils import IN_BROWSER_PYODIDE
from shimoku.api.client import ApiClient
import inspect

from copy import copy

logger = logging.getLogger(__name__)

if not IN_BROWSER_PYODIDE:
    nest_asyncio.apply()


class AsyncGroup(ABC):
    """
    Class to define the async groups. It is used to avoid conflicts between tasks.
    """

    def __init__(self):
        self.conflicts: set[AsyncGroup] = set()

    def add_conflict(self, group: 'AsyncGroup'):
        self.conflicts.add(group)

    def is_conflicting(self, group: 'AsyncGroup') -> bool:
        return group in self.conflicts or any(
            i_group.is_conflicting(group) for i_group in self.conflicts
        )


general_group = AsyncGroup()


def add_general_async_group(func: Callable):
    """
    This function adds the function to the general async group.
    """
    func.async_group = general_group
    return func


class AutoAsyncExecutionPool:
    """
    This class stores the arguments needed to execute the tasks in the task pool and the methods to execute them.
    It is used to avoid the use of async/await in the user's code.
    """

    ACTIONS_TEST = False

    def __init__(
            self,
            api_client: ApiClient,
    ):
        self.api_client = api_client
        self.ending_tasks: Dict[str, Coroutine] = {}
        self.task_pool = []
        self.free_context = {}
        # By default, set to true, to make the user aware that it is using the async configuration
        # (they will have to explicitly state it in their code)
        self.sequential = True
        self.universe = None
        self.in_async = False
        self._current_groups: list[AsyncGroup] = []

    def clear(self):
        self.ending_tasks = {}
        self.task_pool = []
        self.free_context = {}
        self._current_groups = []

    async def execute_tasks(self) -> list:
        """
        This function executes the tasks in the task pool, and the ending tasks, if any.
        Lastly, it executes the last task in the task pool, and returns its result.
        """
        # IMPORTANT!! Nothing has to be dependent on this code as the sequential execution needs to keep working
        self.api_client.semaphore = asyncio.Semaphore(self.api_client.semaphore_limit)
        # To solve race conditions
        task_pool = copy(self.task_pool)
        self.task_pool.clear()
        results = await asyncio.gather(*task_pool)
        if self.ending_tasks:
            await asyncio.gather(*self.ending_tasks.values())
        self.clear()
        return list(results)

    def auto_async_func_call(
            self,
            func_self: Any,
            func: Callable,
            args: Optional[tuple] = None,
            kwargs: Optional[dict] = None,
            async_group: Optional[AsyncGroup] = None,
            name: Optional[str] = None
    ) -> Union[Any, Coroutine]:
        """
        This function adds the function to the task pool, and executes it if the sequential execution is set to True.
        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        async def separate_final_execute():
            """
            This function executes the last task in the task pool, and returns its result.
            """
            if len(self.task_pool) > 0:
                await self.execute_tasks()
            self.task_pool.append(func(func_self, *args, **kwargs))
            return (await self.execute_tasks())[0]

        conflict = not async_group or any(group.is_conflicting(async_group) for group in self._current_groups)

        if self.sequential or conflict:
            if IN_BROWSER_PYODIDE or self.ACTIONS_TEST:
                # If in pyodide return the coroutine
                return separate_final_execute()
            # If not in an async context, run the event loop
            return asyncio.run(separate_final_execute())

        # Copy the current context to make the execution independent and avoid the modification of the original context
        self.task_pool.append(func(copy(func_self), *args, **kwargs))
        self._current_groups.append(async_group)
        logger.info(f'{func.__name__ if not name else name} added to the task pool')

        if IN_BROWSER_PYODIDE or self.ACTIONS_TEST:
            # If in pyodide return the coroutine
            return asyncio.sleep(0)


def decorate_class_to_auto_async(
    cls: type,
    async_pool: AutoAsyncExecutionPool
) -> Type:
    """
    This function returns the class with all the methods decorated to be handled by the AutoAsyncExecutionPool.
    If the class has a method called _check_before_async_execution, it will be called before the async execution.
    If in PYODIDE execution all the methods will return a coroutine.
    """
    def decorate_to_auto_async(func: Callable):
        """
        This function decorates a method to be handled by the AutoAsyncExecutionPool.
        If the method has a return annotation, it will be executed and returned, if not it will be asummed that
        it can be executed with multiple tasks and will be added to the task pool.
        """
        def wrapper(self, *args, **kwargs):
            if inspect.iscoroutinefunction(func):
                if hasattr(self, '_check_before_async_execution'):
                    self._check_before_async_execution(async_pool, func, *args, **kwargs)
                return async_pool.auto_async_func_call(
                    func=func,
                    args=args,
                    kwargs=kwargs,
                    func_self=self,
                    async_group=func.async_group if hasattr(func, 'async_group') else None
                )
            result = func(self, *args, **kwargs)
            if IN_BROWSER_PYODIDE or async_pool.ACTIONS_TEST:
                # If in pyodide return a wrapper coroutine
                async def result():
                    return result

                return result()
            return result

        return wrapper

    new_class = type(cls.__name__, (cls,), {})
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            setattr(new_class, attr_name, decorate_to_auto_async(attr))

    return new_class
