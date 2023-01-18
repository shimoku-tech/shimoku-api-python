import asyncio
from functools import wraps
from typing import Callable, Tuple


#TODO find a better way to handle this
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
menu_paths = []


def async_auto_call_manager(
        sequential: bool = False, execute: bool = False, task_pool=task_pool, menu_paths=menu_paths,
        get_or_create_app_and_app_type: Callable = None):
    def decorator(async_func):
        async def execute_tasks(*args):
            menu_path_tasks = [get_or_create_app_and_app_type(args[0], name=clean_menu_path(menu_path=menu_path)[0])
                               for menu_path in menu_paths]
            await asyncio.gather(*menu_path_tasks)
            await asyncio.gather(*task_pool)
            task_pool.clear()

        @wraps(async_func)
        def wrapper(*args, **kwargs):
            nonlocal task_pool
            nonlocal menu_paths
            if sequential:
                if len(task_pool) > 0:
                    asyncio.run(execute_tasks(*args))
                return asyncio.run(async_func(*args, **kwargs))
            else:
                task_pool += [async_func(*args, **kwargs)]
                if 'menu_path' in kwargs and kwargs['menu_path'] not in menu_paths:
                    menu_paths += [kwargs['menu_path']]
                if execute:
                    asyncio.run(execute_tasks(*args))

        return wrapper

    return decorator
