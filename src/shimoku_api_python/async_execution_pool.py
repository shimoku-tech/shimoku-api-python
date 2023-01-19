import asyncio
from functools import wraps
from inspect import getmembers
from typing import Callable, Tuple


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
sequential = False


def activate_sequential_execution():
    global sequential
    sequential = True


def deactivate_sequential_execution():
    global sequential
    sequential = False


def async_auto_call_manager(
        execute: bool = False, get_or_create_app_and_app_type: Callable = None):
    def decorator(async_func):

        async def execute_tasks(*args):
            # TODO This solution has to be solved, passing the function complicates without necessity
            if get_or_create_app_and_app_type:
                # we need to create the apps before the tasks try to access them all at once
                menu_path_tasks = [get_or_create_app_and_app_type(args[0], name=app_name) for app_name in app_names]
                await asyncio.gather(*menu_path_tasks)
            results = await asyncio.gather(*task_pool)
            task_pool.clear()
            return results[-1]

        @wraps(async_func)
        def wrapper(*args, **kwargs):

            if sequential:
                return asyncio.run(async_func(*args, **kwargs))

            global task_pool, app_names
            task_pool.append(async_func(*args, **kwargs))
            if 'menu_path' in kwargs:
                app_name = clean_menu_path(menu_path=kwargs['menu_path'])[0]
                app_names += [app_name] if app_name not in app_names else []
            if execute:
                return asyncio.run(execute_tasks(*args))

        return wrapper

    return decorator
