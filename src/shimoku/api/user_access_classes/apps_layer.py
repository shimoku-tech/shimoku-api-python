from typing import Optional
import asyncio

from shimoku.api.resources.role import (
    user_delete_role,
    user_get_role,
    user_get_roles,
    user_create_role,
)
from shimoku.utils import create_normalized_name
from shimoku.api.resources.app import App
from shimoku.api.resources.business import Business
from shimoku.api.resources.activity import Activity

import logging
from shimoku.execution_logger import ClassWithLogging

logger = logging.getLogger(__name__)


class MenuPathsLayer(ClassWithLogging):
    """
    This class is used to interact with the API at the Menu Path level.
    """

    _module_logger = logger
    _use_info_logging = True

    def __init__(
        self,
        business: Business,
    ):
        self._business = business
        self._get_for_roles = self._business.get_app if business else None

    async def _get_app_with_warning(
        self, name: Optional[str] = None, uuid: Optional[str] = None
    ) -> Optional[App]:
        """
        Get the menu path metadata
        :param name: name of the menu path
        :param uuid: UUID of the menu path
        :return: The menu path object
        """
        app: App = await self._business.get_app(
            name=name, uuid=uuid, create_if_not_exists=False
        )
        if not app:
            logger.warning(f"Menu path ({name}) not found")
        return app

    async def get_menu_path(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> dict:
        """
        Get a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        :return: menu path metadata
        """
        return (await self._business.get_app(uuid=uuid, name=name)).cascade_to_dict()

    async def update_menu_path(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        new_name: Optional[str] = None,
        hide_title: Optional[bool] = None,
        hide_path: Optional[bool] = None,
        show_breadcrumb: Optional[bool] = None,
        show_history_navigation: Optional[bool] = None,
        order: Optional[int] = None,
    ) -> bool:
        """
        Update a menu path
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
            uuid=uuid,
            name=name,
            new_name=new_name,
            normalizedName=create_normalized_name(new_name) if new_name else None,
            hideTitle=hide_title,
            hidePath=hide_path,
            showBreadcrumb=show_breadcrumb,
            showHistoryNavigation=show_history_navigation,
            order=order,
        )

    async def delete_menu_path(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> bool:
        """
        Delete a menu path
        :param uuid: uuid of the menu path
        :param name:
        """
        return await self._business.delete_app(uuid=uuid, name=name)

    async def get_menu_path_activities(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> list[dict]:
        """
        Get the activities of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return []
        return [activity.cascade_to_dict() for activity in await app.get_activities()]

    async def delete_all_menu_path_activities(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        with_linked_to_templates: Optional[bool] = False,
    ) -> bool:
        """
        Delete all activities of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        :param with_linked_to_templates: if True, delete all activities, even those linked to templates
        """
        app = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return False
        activities: list[Activity] = await app.get_activities()
        if not with_linked_to_templates:
            previous_len_activities = len(activities)
            activities = [
                activity
                for activity in activities
                if not activity["activityTemplateWithMode"]
            ]
            if len(activities) != previous_len_activities:
                logger.warning(
                    "Some activities are linked to templates and will not be deleted. To delete them, "
                    "use the (with_linked_to_templates) parameter set to True."
                )
        await asyncio.gather(
            *[app.delete_activity(uuid=activity["id"]) for activity in activities]
        )
        return True

    async def get_menu_path_components(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> list[dict]:
        """
        Get the reports of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return []
        return [report.cascade_to_dict() for report in await app.get_reports()]

    async def delete_all_menu_path_components(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        sub_path: Optional[str] = None,
    ) -> bool:
        """
        Delete all reports of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        :param sub_path: sub path of the menu path
        """
        app = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return False
        reports = await app.get_reports()
        if sub_path:
            reports = [report for report in reports if report["path"] == sub_path]
            if not reports:
                logger.warning(f"Sub path ({sub_path}) not found in menu path ({name})")
                return False
        await asyncio.gather(
            *[app.delete_report(uuid=report["id"]) for report in reports]
        )
        return True

    async def get_menu_path_data_sets(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> list[dict]:
        """
        Get the datasets of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return []
        return [data_set.cascade_to_dict() for data_set in await app.get_data_sets()]

    async def delete_all_menu_path_data_sets(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> bool:
        """
        Delete all datasets of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return False
        data_sets = await app.get_data_sets()
        await asyncio.gather(
            *[app.delete_data_set(uuid=data_set["id"]) for data_set in data_sets]
        )
        return True

    async def get_menu_path_sub_paths(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> list[str]:
        """
        Get the path names of an menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        app: Optional[App] = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return []
        return await app.get_paths_in_order()

    async def get_menu_path_files(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        with_shimoku_generated: Optional[bool] = False,
    ) -> list[dict]:
        """
        Get the files of an menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        :param with_shimoku_generated: whether the file is generated internally by the SDK
        """
        app: Optional[App] = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return []
        files = await app.get_files()
        if not with_shimoku_generated:
            files = [file for file in files if "shimoku_generated" not in file["tags"]]
        return [file.cascade_to_dict() for file in files]

    async def delete_all_menu_path_files(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        with_shimoku_generated: Optional[bool] = False,
    ) -> bool:
        """
        Delete all files of an menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        :param with_shimoku_generated: whether the file is generated internally by the SDK
        """
        app: Optional[App] = await self._get_app_with_warning(uuid=uuid, name=name)
        if not app:
            return False
        files = await app.get_files()
        if not with_shimoku_generated:
            previous_len_files = len(files)
            files = [file for file in files if "shimoku_generated" not in file["tags"]]
            if len(files) != previous_len_files:
                logger.warning(
                    "Some files are generated internally by the SDK and will not be deleted. To delete them, "
                    "use the (with_shimoku_generated) parameter set to True."
                )
        await asyncio.gather(*[app.delete_file(uuid=file["id"]) for file in files])
        return True

    # Role management
    get_role = user_get_role
    get_roles = user_get_roles
    create_role = user_create_role
    delete_role = user_delete_role
