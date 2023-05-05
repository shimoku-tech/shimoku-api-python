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
    async def _get_app_with_warning(self, menu_path: Optional[str] = None, uuid: Optional[str] = None
                                    ) -> Optional[App]:
        """ Get the business
        :param menu_path: name of the app
        :param uuid: UUID of the app
        """
        app: App = await self._business.get_app(menu_path=menu_path, uuid=uuid, create_if_not_exists=False)
        if not app:
            logger.warning(f"App from {menu_path} not found")
        return app

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_app(self, uuid: Optional[str] = None, menu_path: Optional[str] = None) -> Dict:
        """ Create an app
        :param uuid: uuid of the app
        :param menu_path: menu path in use
        """
        return (await self._business.get_app(uuid=uuid, menu_path=menu_path)).cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def update_app(self, uuid: Optional[str] = None, menu_path: Optional[str] = None,
                         new_name: Optional[str] = None, hide_title: Optional[bool] = None,
                         hide_path: Optional[bool] = None, show_breadcrumb: Optional[bool] = None,
                         show_history_navigation: Optional[bool] = None, order: Optional[int] = None):
        """ Create an app
        :param uuid: uuid of the app
        :param menu_path: menu path in use
        :param new_name: new name of the app
        :param hide_title: hide title of the app
        :param hide_path: hide path of the app
        :param show_breadcrumb: show breadcrumb of the app
        :param show_history_navigation: show history navigation of the app
        :param order: order of the app in the side menu
        :return: app metadata
        """
        return await self._business.update_app(
            uuid=uuid, menu_path=menu_path, new_name=new_name,
            normalizedName=create_normalized_name(new_name) if new_name else None,
            hideTitle=hide_title, hidePath=hide_path,
            showBreadcrumb=show_breadcrumb,
            showHistoryNavigation=show_history_navigation,
            order=order
        )

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_app(self, uuid: Optional[str] = None, menu_path: Optional[str] = None):
        """ Delete an app
        :param uuid: uuid of the app
        :param menu_path: menu path in use
        """
        return await self._business.delete_app(uuid=uuid, menu_path=menu_path)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_app_activities(self, uuid: Optional[str] = None, menu_path: Optional[str] = None) -> List[Dict]:
        """ Get the activities of an app
        :param uuid: uuid of the app
        :param menu_path: menu path in use
        """
        app = await self._get_app_with_warning(uuid=uuid, menu_path=menu_path)
        if not app:
            return []
        return [activity.cascade_to_dict() for activity in await app.get_activities()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_app_activities(self, uuid: Optional[str] = None, menu_path: Optional[str] = None):
        """ Delete all activities of an app
        :param uuid: uuid of the app
        :param menu_path: menu path in use
        """
        app = await self._get_app_with_warning(uuid=uuid, menu_path=menu_path)
        if not app:
            return
        await asyncio.gather(*[app.delete_activity(uuid=activity['id']) for activity in await app.get_activities()])

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_app_reports(self, uuid: Optional[str] = None, menu_path: Optional[str] = None) -> List[Dict]:
        """ Get the reports of an app
        :param uuid: uuid of the app
        :param menu_path: menu path in use
        """
        app = await self._get_app_with_warning(uuid=uuid, menu_path=menu_path)
        if not app:
            return []
        return [report.cascade_to_dict() for report in await app.get_reports()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_app_reports(self, uuid: Optional[str] = None, menu_path: Optional[str] = None):
        """ Delete all reports of an app
        :param uuid: uuid of the app
        :param menu_path: menu path in use
        """
        app = await self._get_app_with_warning(uuid=uuid, menu_path=menu_path)
        if not app:
            return
        await asyncio.gather(*[app.delete_report(uuid=report['id']) for report in await app.get_reports()])

    # Role management
    get_role = user_get_role
    get_roles = user_get_roles
    create_role = user_create_role
    delete_role = user_delete_role

