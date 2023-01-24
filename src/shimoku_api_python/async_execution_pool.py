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
tabs_group_indexes = []
sequential = False
plot_api = None


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
            global plot_api

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

            await asyncio.gather(*(task_pool[:-1]))
            result = await task_pool[-1]
            task_pool.clear()

            # After all the tasks have finished update the tabs to get all the charts
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

            return result

        @wraps(async_func)
        def wrapper(*args, **kwargs):

            if sequential:
                return asyncio.run(async_func(*args, **kwargs))

            global task_pool, app_names, tabs_group_indexes
            task_pool.append(async_func(*args, **kwargs))
            if 'menu_path' in kwargs and 'delete' not in async_func.__name__:
                app_name, path_name = clean_menu_path(menu_path=kwargs['menu_path'])
                if not path_name:
                    path_name = ''  # because of tabs

                app_names += [app_name] if app_name not in app_names else []
                if 'tabs_index' in kwargs:
                    tabs_group_pseudo_entry = (app_name, path_name, kwargs['tabs_index'][0])
                    tabs_group_indexes += [tabs_group_pseudo_entry] \
                        if tabs_group_pseudo_entry not in tabs_group_indexes else []

            if execute:
                return asyncio.run(execute_tasks())

        return wrapper

    return decorator
