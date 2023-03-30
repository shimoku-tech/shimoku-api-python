import asyncio
from functools import wraps
from typing import Tuple, Optional, Callable, Coroutine
import logging
from IPython.lib import backgroundjobs as bg
import time
from shimoku_api_python.execution_logger import logging_before_and_after, log_error

from copy import copy
logger = logging.getLogger(__name__)


# TODO find a better way to handle this
def clean_menu_path(menu_path: str) -> Tuple[str, str]:
    """Break the menu path in the apptype or app normalizedName
    and the path normalizedName if any"""
    # remove empty spaces
    menu_path: str = menu_path.strip()
    # replace "_" for www protocol it is not good
    menu_path = menu_path.replace('_', '-')

    try:
        assert len(menu_path.split('/')) <= 2  # we allow only one level of path
    except AssertionError:
        raise ValueError(
            f'We only allow one subpath in your request | '
            f'you introduced {menu_path} it should be maximum '
            f'{"/".join(menu_path.split("/")[:1])}'
        )

    # Split AppType or App Normalized Name
    normalized_name: str = menu_path.split('/')[0]
    name: str = (
        ' '.join(normalized_name.split('-'))
    )

    try:
        path_normalized_name: str = menu_path.split('/')[1]
        path_name: str = (
            ' '.join(path_normalized_name.split('-'))
        )
    except IndexError:
        path_name = None

    return name, path_name


class ExecutionPoolContext:
    """
    This class stores the arguments needed to execute the tasks in the task pool
    """

    def __init__(self, api_client):
        self.api_client = api_client
        self.task_pool = []
        self.tabs_group_indexes = []
        self.list_for_conflicts = []
        # By default, set to true, to make the user aware that it is using the async configuration
        # (they will have to explicitly state it in their code)
        self.sequential = True
        self.plot_api = None


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

        async def execute_tasks(epc: ExecutionPoolContext):
            # IMPORTANT!! Nothing has to be dependent on this code as the sequential execution needs to keep working
            epc.api_client.semaphore = asyncio.Semaphore(epc.api_client.semaphore_limit)
            epc.api_client.locks = {name: asyncio.Lock() for name in epc.api_client.locks.keys()}

            # if just one task it's the same as sequential
            if len(epc.task_pool) == 1:
                result = await epc.task_pool[0]
                epc.task_pool.clear()
                epc.tabs_group_indexes.clear()
                epc.list_for_conflicts.clear()
                return result

            await asyncio.gather(*epc.task_pool)
            epc.task_pool.clear()
            epc.list_for_conflicts.clear()

            # After all the tasks have finished update the tabs to get all the charts correctly
            if len(epc.tabs_group_indexes) > 0:
                tabs_tasks = []
                for tabs_group_pseudo_entry in epc.tabs_group_indexes:
                    app_name, path_name, group_name = tabs_group_pseudo_entry
                    app = await epc.plot_api._plot_aux._async_get_or_create_app_and_apptype(name=app_name)
                    app_id: str = app['id']
                    tabs_tasks.append(
                        epc.plot_api._update_tabs_group_metadata(
                            business_id=epc.plot_api.business_id,
                            app_id=app_id, path_name=path_name,
                            group_name=group_name,
                        )
                    )

                await asyncio.gather(*tabs_tasks)
                epc.tabs_group_indexes.clear()

        async def sequential_task_execution(epc: ExecutionPoolContext, coroutine: Coroutine):
            epc.api_client.semaphore = asyncio.Semaphore(epc.api_client.semaphore_limit)
            epc.api_client.locks = {name: asyncio.Lock() for name in epc.api_client.locks.keys()}
            return await coroutine

        @wraps(async_func)
        def wrapper(self, *args, **kwargs):

            # Get the epc from the self argument, it's always the first element of the args
            if hasattr(self, 'epc'):
                epc: ExecutionPoolContext = self.epc
            else:
                log_error(logger, 'The async_auto_call_manager decorator can only be used in classes that '
                                  'have an epc attribute', RuntimeError)

            epc.plot_api._plot_aux.app_metadata_api.apps = {}
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
                        while not job.finished:
                            time.sleep(0.1)

                    job = jobs.new(asyncio.run, sequential_task_execution(epc, async_func(self, *args, **kwargs)))
                    while not job.finished:
                        time.sleep(0.1)

                    return job.result
                else:
                    if len(epc.task_pool) > 0:
                        logger.info('Executing task pool')
                        asyncio.run(execute_tasks(epc))
                    return asyncio.run(sequential_task_execution(epc, async_func(self, *args, **kwargs)))

            _self = copy(self)  # copy the self object to avoid modifying the shallow data
            epc.task_pool.append(async_func(_self, *args, **kwargs))
            logger.info(f'{async_func.__name__} added to the task pool')

            if kwargs.get('menu_path') and 'delete' not in async_func.__name__:
                app_name, path_name = clean_menu_path(menu_path=kwargs['menu_path'])
                if not path_name:
                    path_name = ''  # because of tabs

                list_for_conflicts_entry = app_name + path_name

                tabs_index = kwargs.get('tabs_index')
                modal_name = kwargs.get('modal_name')
                order = kwargs.get('order')

                if modal_name is not None and tabs_index:
                    log_error(logger,
                              'The modal_name and tabs_index parameters can not be used at the same time',
                              RuntimeError)

                if modal_name is not None:
                    list_for_conflicts_entry += modal_name
                elif tabs_index:
                    list_for_conflicts_entry += tabs_index[0] + tabs_index[1]
                    tabs_group_pseudo_entry = (app_name, path_name, tabs_index[0])
                    epc.tabs_group_indexes += [tabs_group_pseudo_entry] \
                        if tabs_group_pseudo_entry not in epc.tabs_group_indexes else []

                if order is not None:
                    list_for_conflicts_entry += str(order)

                    if list_for_conflicts_entry in epc.list_for_conflicts:
                        epc.task_pool.clear()
                        epc.tabs_group_indexes.clear()
                        epc.list_for_conflicts.clear()
                        log_error(logger, 'Report order collision, two reports with the same order can not be executed '
                                          'at the same time', RuntimeError)
                    else:
                        epc.list_for_conflicts.append(list_for_conflicts_entry)

        return wrapper

    return decorator
