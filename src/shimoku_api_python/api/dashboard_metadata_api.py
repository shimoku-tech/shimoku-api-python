from typing import Dict, Optional, List, Union

import asyncio

from uuid import uuid1

from ..async_execution_pool import async_auto_call_manager, ExecutionPoolContext
from ..resources.role import user_delete_role, user_get_role, user_get_roles, user_create_role

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
    async def create_board(
        self, name: str, order: Optional[int] = None,
        is_public: bool = False, is_disabled: bool = False
    ) -> Dict:
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
    async def _get_dashboard_with_warning(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> Optional[Dashboard]:
        """ Get the dashboard metadata
        :param name: name of the dashboard
        :param uuid: UUID of the dashboard
        :return: The dashboard object
        """
        dashboard: Dashboard = await self._business.get_dashboard(uuid=uuid, name=name, create_if_not_exists=False)
        if not dashboard:
            logger.warning(f"Board with name {name} not found, not doing anything")
        return dashboard

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_board(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> Optional[Dict]:
        """ Get the board metadata
        :param name: name of the board
        :param uuid: UUID of the board
        :return: board metadata
        """
        dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)
        if not dashboard:
            return None
        return dashboard.cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_board(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """ Delete a board
        :param name: name of the board
        :param uuid: UUID of the board
        """
        await self._business.delete_dashboard(uuid=uuid, name=name)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def update_board(
        self, uuid: Optional[str] = None, name: Optional[str] = None,
        new_name: Optional[str] = None, order: Optional[int] = None,
        is_public: Optional[bool] = None, is_disabled: Optional[bool] = None
    ):
        """ Update a board
        :param new_name: name of the board
        :param uuid: UUID of the board
        :param name: new name of the board
        :param order: new order of the board
        :param is_public: new public permission of the board
        :param is_disabled: new is_disabled of the board
        """
        await self._business.update_dashboard(
            uuid=uuid, name=name, new_name=new_name, order=order,
            is_disabled=is_disabled,
            publicPermission={
                'isPublic': is_public,
                'permission': 'READ',
                'token': str(uuid1())
            } if is_public is not None else None
        )

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def is_menu_path_in_board(
        self, menu_path_name: Optional[str] = None, menu_path_id: Optional[str] = None,
        uuid: Optional[str] = None, name: Optional[str] = None
    ) -> bool:
        """ Check if an app is in a board
        :param menu_path_name: name of the menu path
        :param menu_path_id: UUID of the menu path
        :param name: name of the board
        :param uuid: UUID of the board
        :return: True if the app is in the board, False otherwise
        """
        dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)

        if dashboard:
            app = await self._business.get_app(name=menu_path_name, uuid=menu_path_id, create_if_not_exists=False)
            if not app:
                return False
            return menu_path_id in await dashboard.list_app_ids()
        return False

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def add_menu_path_in_board(
        self, menu_path_name: Optional[str] = None, menu_path_id: Optional[str] = None,
        uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """ Add an app in a board
        :param menu_path_name: name of the menu path
        :param menu_path_id: UUID of the menu path
        :param name: name of the board
        :param uuid: UUID of the board
        """
        dashboard = await self._business.get_dashboard(uuid=uuid, name=name)

        app = await self._business.get_app(name=menu_path_name, uuid=menu_path_id)

        if app['id'] in await dashboard.list_app_ids():
            logger.info(f"Menu path {str(app)} already in board {str(dashboard)}, not doing anything")
            return

        await dashboard.insert_app(app)

        logger.info(f"Menu path {str(app)} added to board {str(dashboard)}")

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def remove_menu_path_from_board(
        self, menu_path_name: Optional[str] = None, menu_path_id: Optional[str] = None,
        uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """ Remove an app from a board
        :param menu_path_name: name of the menu path
        :param menu_path_id: UUID of the menu path
        :param name: name of the board
        :param uuid: UUID of the board
        """

        dashboard: Dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)

        if dashboard:
            app = await self._business.get_app(name=menu_path_name, uuid=menu_path_id, create_if_not_exists=False)
            if not app:
                logger.warning(f"Menu path {menu_path_name if menu_path_name else menu_path_id} "
                               f"not found, not doing anything")
                return

            await dashboard.remove_app(app)
            logger.info(f"Deleted link between menu path {str(app)} and board {str(dashboard)}")

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def remove_all_menu_paths_from_board(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """ Delete all menu paths links of a board
        :param name: name of the board
        :param uuid: UUID of the board
        """
        dashboard: Dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)

        if dashboard:
            await dashboard.remove_all_apps()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def group_menu_paths(
        self, menu_path_names: Union[Optional[List[str]], str] = None, menu_path_ids: Optional[List[str]] = None,
        uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """ Add multiple menu paths in a board, if the board does not exist create it
        :param menu_path_names: list of menu path names
        :param menu_path_ids: list of menu path UUIDs
        :param name: name of the board
        :param uuid: UUID of the board
        """

        dashboard = await self._business.get_dashboard(uuid=uuid, name=name)

        apps = []
        if menu_path_names:
            if isinstance(menu_path_names, list):
                apps = await asyncio.gather(*[self._business.get_app(name=menu_path) for menu_path in menu_path_names])
            elif menu_path_names == 'all':
                apps = await self._business.get_apps()
        elif menu_path_ids:
            apps = await asyncio.gather(*[self._business.get_app(uuid=app_id) for app_id in menu_path_ids])

        if not apps:
            logger.warning('No menu paths have been provided, not doing anything')
            return

        await asyncio.gather(*[dashboard.insert_app(app=app) for app in apps])

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_board_menu_path_ids(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> List[str]:
        """ Get the list of the ids of the menu paths in the board
        :param name: name of the board
        :param uuid: UUID of the board
        :return: list of the ids of the menu paths in the board
        """
        dashboard: Dashboard = await self._get_dashboard_with_warning(uuid=uuid, name=name)

        if dashboard:
            return await dashboard.list_app_ids()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def force_delete_board(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """ Force delete a board, this will delete the links between the board and the menu paths first, so that
        the board can always be deleted, but the apps will not be deleted
        :param name: name of the board
        :param uuid: UUID of the board
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
