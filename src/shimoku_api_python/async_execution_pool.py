import asyncio
from functools import wraps
from inspect import getmembers
from typing import Tuple, Optional


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
app_metadata_api = None


def activate_sequential_execution():
    global sequential
    sequential = True


def deactivate_sequential_execution():
    global sequential
    sequential = False


def async_auto_call_manager(
        execute: Optional[bool] = False):
    def decorator(async_func):

        async def execute_tasks():
            global app_metadata_api
            # we need to create the apps before the tasks try to access them all at once
            if app_names:
                menu_path_tasks = [app_metadata_api.get_or_create_app_and_apptype(name=app_name)
                                   for app_name in app_names]
                await asyncio.gather(*menu_path_tasks)
                app_names.clear()
            await asyncio.gather(*(task_pool[:-1]))
            result = await task_pool[-1]
            task_pool.clear()

            return result

        @wraps(async_func)
        def wrapper(*args, **kwargs):

            if sequential:
                return asyncio.run(async_func(*args, **kwargs))

            global task_pool, app_names
            task_pool.append(async_func(*args, **kwargs))
            if 'menu_path' in kwargs and 'delete' not in async_func.__name__:
                app_name = clean_menu_path(menu_path=kwargs['menu_path'])[0]
                app_names += [app_name] if app_name not in app_names else []
            if execute:
                return asyncio.run(execute_tasks())

        return wrapper

    return decorator
