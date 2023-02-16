import asyncio
from functools import wraps
from typing import Tuple, Optional, Callable, Coroutine
import logging
from IPython.lib import backgroundjobs as bg
import time


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


task_pool = []
app_names = []
tabs_group_indexes = []
list_for_conflicts = []
# By default, set to true, to make the user aware that it is using the async configuration
# (they will have to explicitly state it in their code)
sequential = True
plot_api = None
api_client = None
logger = logging.getLogger(__name__)


def activate_sequential_execution():
    global sequential
    sequential = True


def deactivate_sequential_execution():
    global sequential
    sequential = False


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

        async def execute_tasks():
            # IMPORTANT!! Nothing has to be dependent on this code as the sequential execution needs to keep working
            global plot_api
            api_client.semaphore = asyncio.Semaphore(api_client.semaphore_limit)

            # if just one task it's the same as sequential
            if len(task_pool) == 1:
                result = await task_pool[0]
                task_pool.clear()
                app_names.clear()
                tabs_group_indexes.clear()
                list_for_conflicts.clear()
                return result

            # We need to create the apps before the tasks try to access them all at once
            if len(app_names) > 0:
                menu_path_tasks = [plot_api._plot_aux.get_or_create_app_and_apptype(name=app_name)
                                   for app_name in app_names]
                await asyncio.gather(*menu_path_tasks)
                app_names.clear()

            # After the apps are created we need to create the tabs to not create multiple tabs
            if len(tabs_group_indexes) > 0:
                tabs_tasks = []
                for tabs_group_pseudo_entry in tabs_group_indexes:
                    app_name, path_name, group_name = tabs_group_pseudo_entry
                    app = await plot_api._plot_aux.get_or_create_app_and_apptype(name=app_name)
                    app_id: str = app['id']
                    tabs_group_entry = (app_id, path_name, group_name)
                    if tabs_group_entry not in plot_api._tabs:
                        tabs_tasks.append(plot_api._create_tabs_group(plot_api.business_id, tabs_group_entry))

                await asyncio.gather(*tabs_tasks)

            await asyncio.gather(*task_pool)
            task_pool.clear()
            list_for_conflicts.clear()

            # After all the tasks have finished update the tabs to get all the charts correctly
            if len(tabs_group_indexes) > 0:
                tabs_tasks = []
                for tabs_group_pseudo_entry in tabs_group_indexes:
                    app_name, path_name, group_name = tabs_group_pseudo_entry
                    app = await plot_api._plot_aux.get_or_create_app_and_apptype(name=app_name)
                    app_id: str = app['id']
                    tabs_tasks.append(
                        plot_api._update_tabs_group_metadata(
                            business_id=plot_api.business_id,
                            app_id=app_id, path_name=path_name,
                            group_name=group_name,
                        )
                    )

                await asyncio.gather(*tabs_tasks)
                tabs_group_indexes.clear()

        async def sequential_task_execution(coroutine: Coroutine):
            api_client.semaphore = asyncio.Semaphore(api_client.semaphore_limit)
            return await coroutine

        @wraps(async_func)
        def wrapper(*args, **kwargs):

            global task_pool, app_names, tabs_group_indexes

            if sequential or execute:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    # We are in a jupyter notebook, so we need to execute in a different loop
                    jobs = bg.BackgroundJobManager()
                    if len(task_pool) > 0:
                        logger.info('Executing task pool')
                        job = jobs.new(asyncio.run, execute_tasks())
                        while not job.finished:
                            time.sleep(0.1)

                    job = jobs.new(asyncio.run, async_func(*args, **kwargs))
                    while not job.finished:
                        time.sleep(0.1)

                    return job.result
                else:
                    if len(task_pool) > 0:
                        logger.info('Executing task pool')
                        asyncio.run(execute_tasks())
                    return asyncio.run(sequential_task_execution(async_func(*args, **kwargs)))

            task_pool.append(async_func(*args, **kwargs))
            logger.info(f'{async_func.__name__} added to the task pool')

            if kwargs.get('menu_path') and 'delete' not in async_func.__name__:
                app_name, path_name = clean_menu_path(menu_path=kwargs['menu_path'])
                if not path_name:
                    path_name = ''  # because of tabs

                list_for_conflicts_entry = app_name + path_name

                app_names += [app_name] if app_name not in app_names else []
                if kwargs.get('tabs_index'):
                    list_for_conflicts_entry += kwargs['tabs_index'][0] + kwargs['tabs_index'][1]
                    tabs_group_pseudo_entry = (app_name, path_name, kwargs['tabs_index'][0])
                    tabs_group_indexes += [tabs_group_pseudo_entry] \
                        if tabs_group_pseudo_entry not in tabs_group_indexes else []

                if kwargs.get('order'):
                    list_for_conflicts_entry += str(kwargs.get('order'))

                    if list_for_conflicts_entry in list_for_conflicts:
                        task_pool.clear()
                        app_names.clear()
                        tabs_group_indexes.clear()
                        list_for_conflicts.clear()
                        error_message = 'Report order collision, two reports with the same order can not be executed ' \
                                        'at the same time'
                        logger.error(error_message)
                        raise RuntimeError(error_message)
                    else:
                        list_for_conflicts.append(list_for_conflicts_entry)

        return wrapper

    return decorator
