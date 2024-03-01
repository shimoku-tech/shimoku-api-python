import asyncio

from typing import Optional

from shimoku.api.resources.role import (
    user_delete_role,
    user_get_role,
    user_get_roles,
    user_create_role,
)
from shimoku.api.resources.business import Business
from shimoku.api.resources.app import App
from shimoku.api.resources.report import Report
from shimoku.api.resources.universe import Universe
from shimoku.utils import create_normalized_name
from shimoku.exceptions import WorkspaceError

import logging
from shimoku.execution_logger import log_error, ClassWithLogging

logger = logging.getLogger(__name__)


class WorkspacesLayer(ClassWithLogging):
    """
    This class is used to interact with the API at the Workspace layer
    """

    _module_logger = logger
    _use_info_logging = True

    def __init__(
        self,
        universe: Universe,
    ):
        self._universe = universe
        self._get_for_roles = self._get_business_with_warning

    async def _check_similar_name(self, name: str):
        """
        Check if there is a workspace with a similar name
        :param name: name of the workspace
        """
        all_business = await self._universe.get_businesses()
        normalized_name = create_normalized_name(name)
        if normalized_name in [
            create_normalized_name(business["name"]) for business in all_business
        ]:
            log_error(
                logger,
                "There exists a workspace with a very similar name, please choose another name",
                WorkspaceError,
            )

    async def _get_business_with_warning(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> Optional[Business]:
        """
        Get a workspace with a warning if it does not exist
        :param name: name of the workspace
        :param uuid: uuid of the workspace
        """
        business: Business = await self._universe.get_business(uuid=uuid, name=name)
        if not business:
            logger.warning(f"Workspace ({name if name else uuid}) not found")
        return business

    async def create_workspace(
        self, name: str, create_default_roles: bool = True, theme: Optional[dict] = None
    ) -> dict:
        """Create a new workspace and the necessary roles if specified
        :param name: Name of the workspace
        :param create_default_roles: Create the default roles for the workspace
        :param theme: Theme of the workspace
        :return: workspace data
        """
        await self._check_similar_name(name)

        business = await self._universe.create_business(name=name, theme=theme)
        logger.info(f"Created workspace ({str(business)})")

        if create_default_roles:
            create_roles_tasks = []

            for role_permission_resource in [
                "DATA",
                "DATA_EXECUTION",
                "USER_MANAGEMENT",
                "BUSINESS_INFO",
            ]:
                create_roles_tasks.append(
                    business.create_role(
                        role="business_read",
                        resource=role_permission_resource,
                    )
                )

            await asyncio.gather(*create_roles_tasks)
            logger.info(f"Created default roles for workspace ({str(business)})")

        return business.cascade_to_dict()

    async def update_workspace(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        new_name: Optional[str] = None,
        theme: Optional[dict] = None,
    ) -> bool:
        """Update a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param new_name: New name of the workspace
        :param theme: New theme of the workspace
        :return: True if the workspace was updated
        """
        params = {}

        if new_name is not None:
            await self._check_similar_name(new_name)
            params["new_name"] = new_name

        if isinstance(theme, dict):
            params["theme"] = theme

        return await self._universe.update_business(uuid=uuid, name=name, **params)

    async def delete_workspace(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> bool:
        """Delete a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: True if the workspace was deleted
        """
        return await self._universe.delete_business(uuid=uuid, name=name)

    async def get_workspace(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> dict:
        """Get a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: Workspace data
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return {}
        return business.cascade_to_dict()

    async def get_workspace_menu_paths(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> list[dict]:
        """Get the menu paths of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: list of apps
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return []
        return [app.cascade_to_dict() for app in await business.get_apps()]

    async def get_workspace_menu_path_ids(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> list[dict]:
        """Get the menu path ids of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: list of app ids
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return []
        return [app["id"] for app in await business.get_apps()]

    async def get_workspace_boards(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> list[dict]:
        """Get the boards of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: list of dashboards
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return []
        return [
            dashboard.cascade_to_dict() for dashboard in await business.get_dashboards()
        ]

    async def delete_all_workspace_menu_paths(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """Delete all menu paths of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return
        apps = await business.get_apps()
        await asyncio.gather(*[business.delete_app(uuid=app["id"]) for app in apps])

    async def delete_all_workspace_boards(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        force: bool = False,
    ):
        """Delete all boards of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param force: Flag to force delete the boards
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return
        dashboards = await business.get_dashboards()
        if force:
            await asyncio.gather(
                *[dashboard.remove_all_apps() for dashboard in dashboards]
            )
        await asyncio.gather(
            *[
                business.delete_dashboard(uuid=dashboard["id"])
                for dashboard in dashboards
            ]
        )

    async def change_boards_order(
        self,
        boards: list[str],
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Change the order of the boards of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param boards: list of dashboard names
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return
        await asyncio.gather(
            *[
                business.update_dashboard(name=d_name, order=i + 1)
                for i, d_name in enumerate(boards)
            ]
        )

    @staticmethod
    async def _change_sub_paths_order(
        business: Business, menu_path: str, sub_paths: list[str]
    ):
        """
        Change the order of the sub paths of a menu path
        :param business: Business object
        :param menu_path: Menu path name
        :param sub_paths: list of sub paths
        """
        app: App = await business.get_app(name=menu_path, create_if_not_exists=False)
        if not app:
            logger.warning(f"Menu path ({menu_path}) not found")
            return
        reports: list[Report] = await app.get_reports()
        sub_paths = [create_normalized_name(sub_path) for sub_path in sub_paths]
        non_referenced_reports = sorted(
            [
                report
                for report in reports
                if report["path"] is not None
                and create_normalized_name(report["path"]) not in sub_paths
            ],
            key=lambda x: x["pathOrder"],
        )
        for report in non_referenced_reports:
            sub_path = report["path"]
            if sub_path not in sub_paths:
                sub_paths.append(sub_path)

        tasks = []
        for i, sub_path in enumerate(sub_paths):
            _reports = [
                report
                for report in reports
                if (
                    report["path"] is not None
                    and create_normalized_name(report["path"])
                    == create_normalized_name(sub_path)
                )
            ]
            for report in _reports:
                tasks.append(app.update_report(uuid=report["id"], pathOrder=i))

        logger.info(f"Updating {len(reports)} components from menu path ({str(app)})")

        await asyncio.gather(*tasks)

    async def change_menu_order(
        self, menu_order: list, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """Change the order of the menu of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param menu_order: list of menu names
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return
        tasks = []
        for i, menu_option in enumerate(menu_order):
            menu_name = menu_option
            if isinstance(menu_option, tuple):
                menu_name, sub_paths = menu_option
                tasks.append(
                    self._change_sub_paths_order(
                        business=business, menu_path=menu_name, sub_paths=sub_paths
                    )
                )
            tasks.append(business.update_app(name=menu_name, order=i))

        await asyncio.gather(*tasks)

    # Role management
    get_role = user_get_role
    get_roles = user_get_roles
    create_role = user_create_role
    delete_role = user_delete_role
