from typing import List, Dict, Optional
import asyncio

from ..resources.role import user_delete_role, user_get_role, user_get_roles, user_create_role
from ..utils import create_normalized_name
from ..resources.business import Business
from ..resources.app import App
from ..async_execution_pool import async_auto_call_manager, ExecutionPoolContext

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class AppMetadataApi:
    """
    AppMetadataApi is a class that contains all the methods to interact with the app metadata in the API
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, business: 'Business', execution_pool_context: ExecutionPoolContext):
        self._business = business
        self.epc = execution_pool_context

        self._get_for_roles = self._business.get_app if business else None

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_app_with_warning(
        self, name: Optional[str] = None, uuid: Optional[str] = None
    ) -> Optional[App]:
        """ Get the business
        :param name: name of the app
        :param uuid: UUID of the app
        """
        app: App = await self._business.get_app(name=name, uuid=uuid, create_if_not_exists=False)
        if not app:
            logger.warning(f"Menu path {name} not found")
        return app

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_menu_path(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> Dict:
        """ Create a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        return (await self._business.get_app(uuid=uuid, name=name)).cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def update_menu_path(
        self, uuid: Optional[str] = None, name: Optional[str] = None,
        new_name: Optional[str] = None, hide_title: Optional[bool] = None,
        hide_path: Optional[bool] = None, show_breadcrumb: Optional[bool] = None,
        show_history_navigation: Optional[bool] = None, order: Optional[int] = None
    ):
        """ Create a menu path
        :param uuid: uuid of the menu path
        :param name: the name of the menu path
        :param new_name: new name of the menu path
        :param hide_title: hide title of the menu path
        :param hide_path: hide path of the menu path
        :param show_breadcrumb: show breadcrumb of the menu path
        :param show_history_navigation: show history navigation of the menu path
        :param order: order of the menu path in the side menu
        :return: menu path metadata
        """
        return await self._business.update_app(
            uuid=uuid, name=name, new_name=new_name,
            normalizedName=create_normalized_name(new_name) if new_name else None,
            hideTitle=hide_title, hidePath=hide_path,
            showBreadcrumb=show_breadcrumb,
            showHistoryNavigation=show_history_navigation,
            order=order
        )

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_menu_path(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """ Delete an app
        :param uuid: uuid of the app
        :param name: 
        """

        return await self._business.delete_app(uuid=uuid, name=name)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_menu_path_activities(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> List[Dict]:
        """ Get the activities of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return []
        return [activity.cascade_to_dict() for activity in await app.get_activities()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_menu_path_activities(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """ Delete all activities of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return
        await asyncio.gather(*[app.delete_activity(uuid=activity['id']) for activity in await app.get_activities()])

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_menu_path_components(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> List[Dict]:
        """ Get the reports of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return []
        return [report.cascade_to_dict() for report in await app.get_reports()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_menu_path_components(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """ Delete all reports of an menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return
        await asyncio.gather(*[app.delete_report(uuid=report['id']) for report in await app.get_reports()])

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_menu_path_sub_paths(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> List[str]:
        """ Get the path names of an menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app: Optional[App] = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return []
        return await app.get_paths_in_order()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_menu_path_files(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> List[Dict]:
        """ Get the files of an menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app: Optional[App] = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return []
        return [file.cascade_to_dict() for file in await app.get_files()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_menu_path_files(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """ Delete all files of an menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app: Optional[App] = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return
        await asyncio.gather(*[app.delete_file(uuid=file['id']) for file in await app.get_files()])

    # Role management
    get_role = user_get_role
    get_roles = user_get_roles
    create_role = user_create_role
    delete_role = user_delete_role

