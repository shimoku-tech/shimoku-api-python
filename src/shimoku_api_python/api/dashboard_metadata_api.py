from typing import Dict, Optional, List, Union

import asyncio

from uuid import uuid1

from ..async_execution_pool import async_auto_call_manager, ExecutionPoolContext
from ..resources.role import user_delete_role, user_get_role, user_get_roles, user_create_role
from ..utils import clean_menu_path
from ..resources.business import Business
from ..resources.dashboard import Dashboard

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class DashboardMetadataApi:
    """
    DashboardMetadataApi is a class that contains all the methods to interact with the dashboard metadata in the API
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, business: 'Business', execution_pool_context: ExecutionPoolContext):
        self._business = business
        self.epc = execution_pool_context

        self._get_for_roles = self._get_dashboard_with_warning

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_dashboard(self, name: str, order: Optional[int] = None,
                               is_public: bool = False, is_disabled: bool = False) -> Dict:
        """ Create a dashboard
        :param name: name of the dashboard
        :param order: order of the dashboard
        :param is_public: is the dashboard public
        :param is_disabled: is the dashboard disabled
        :return: dashboard metadata
        """
        return (await self._business.create_dashboard(
            name=name, order=order if order is not None else len(await self._business.get_dashboards()),
            is_disabled=is_disabled, is_public=is_public
        )).cascade_to_dict()

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_dashboard_with_warning(self, uuid: Optional[str] = None, name: Optional[str] = None
                                          ) -> Optional[Dashboard]:
        """ Get the dashboard metadata
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        :return: The dashboard object
        """
        dashboard: Dashboard = await self._business.get_dashboard(uuid=uuid, name=name, create_if_not_exists=False)
        if not dashboard:
            logger.warning(f"Dashboard with name {name} not found, not doing anything")
        return dashboard

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None) -> Optional[Dict]:
        """ Get the dashboard metadata
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        :return: dashboard metadata
        """
        dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)
        if not dashboard:
            return None
        return dashboard.cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None):
        """ Delete a dashboard
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        """
        await self._business.delete_dashboard(uuid=uuid, name=name)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def update_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None,
                               new_name: Optional[str] = None, order: Optional[int] = None,
                               is_public: Optional[bool] = None, is_disabled: Optional[bool] = None):
        """ Update a dashboard
        :param new_name: name of the dashboard
        :param uuid: UUID of the dashboard
        :param name: new name of the dashboard
        :param order: new order of the dashboard
        :param is_public: new public permission of the dashboard
        :param is_disabled: new is_disabled of the dashboard
        """
        await self._business.update_dashboard(
            uuid=uuid, name=name, new_name=new_name, order=order,
            is_disabled=is_disabled,
            publicPermision={
                'isPublic': is_public,
                'permission': 'READ',
                'token': str(uuid1())
            } if is_public is not None else None
        )

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def is_app_in_dashboard(self, menu_path: Optional[str] = None, app_id: Optional[str] = None,
                                  uuid: Optional[str] = None, name: Optional[str] = None) -> bool:
        """ Check if an app is in a dashboard
        :param menu_path: The menu_path in use
        :param app_id: id of the app to check
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        :return: True if the app is in the dashboard, False otherwise
        """
        dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)

        if dashboard:
            app = await self._business.get_app(menu_path=menu_path, uuid=app_id, create_if_not_exists=False)
            if not app:
                return False
            return app_id in await dashboard.list_app_ids()
        return False

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def add_app_in_dashboard(self, menu_path: Optional[str] = None, app_id: Optional[str] = None,
                                   uuid: Optional[str] = None, name: Optional[str] = None):
        """ Add an app in a dashboard
        :param menu_path: The menu_path in use
        :param app_id: UUID of the app
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        """
        dashboard = await self._business.get_dashboard(uuid=uuid, name=name)

        app = await self._business.get_app(menu_path=menu_path, uuid=app_id)

        if app['id'] in await dashboard.list_app_ids():
            logger.info(f"App {str(app)} already in Dashboard {str(dashboard)}, not doing anything")
            return

        await dashboard.insert_app(app)

        logger.info(f"App {str(app)} added to Dashboard {str(dashboard)}")

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def remove_app_from_dashboard(self, menu_path: Optional[str] = None, app_id: Optional[str] = None,
                                        uuid: Optional[str] = None, name: Optional[str] = None):
        """ Remove an app from a dashboard
        :param menu_path: The menu_path in use
        :param app_id: UUID of the app
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        """

        dashboard: Dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)

        if dashboard:
            app = await self._business.get_app(menu_path=menu_path, uuid=app_id, create_if_not_exists=False)
            if not app:
                app_name, _ = clean_menu_path(menu_path) if menu_path else (None, None)
                logger.warning(f"App {app_name if app_name else app_id} not found, not doing anything")
                return

            await dashboard.remove_app(app)
            logger.info(f"Deleted link between app {str(app)} and dashboard {str(dashboard)}")

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def remove_all_apps_from_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None):
        """ Delete all app links of a dashboard
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        """
        dashboard: Dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)

        if dashboard:
            await dashboard.remove_all_apps()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def group_apps(self, menu_paths: Union[Optional[List[str]], str] = None, app_ids: Optional[List[str]] = None,
                         uuid: Optional[str] = None, name: Optional[str] = None):
        """ Add multiple apps in a dashboard, if the dashboard does not exist create it
        :param menu_paths: the menu paths of the apps in use
        :param app_ids: the UUID of the apps to be grouped
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        """

        dashboard = await self._business.get_dashboard(uuid=uuid, name=name)

        apps = []
        if menu_paths:
            if isinstance(menu_paths, list):
                apps = await asyncio.gather(*[self._business.get_app(menu_path=menu_path) for menu_path in menu_paths])
            elif menu_paths == 'all':
                apps = await self._business.get_apps()
        elif app_ids:
            apps = await asyncio.gather(*[self._business.get_app(uuid=app_id) for app_id in app_ids])

        if not apps:
            logger.warning('No apps have been provided, not doing anything')
            return

        await asyncio.gather(*[dashboard.insert_app(app=app) for app in apps])

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_dashboard_app_ids(self, uuid: Optional[str] = None, name: Optional[str] = None) -> List[str]:
        """ Get the list of the ids of the apps in the dashboard
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        :return: list of the ids of the apps in the dashboard
        """
        dashboard: Dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)

        if dashboard:
            return await dashboard.list_app_ids()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def force_delete_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None):
        """ Force delete a dashboard, this will delete the links between the dashboard and the apps first, so that
        the dashboard can always be deleted, but the apps will not be deleted
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        """
        dashboard: Dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)

        if dashboard:
            await dashboard.remove_all_apps()
            await self._business.delete_dashboard(uuid=uuid, name=name)

    # Role management
    get_role = user_get_role
    get_roles = user_get_roles
    create_role = user_create_role
    delete_role = user_delete_role
