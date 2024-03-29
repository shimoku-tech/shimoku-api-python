from typing import Optional, TYPE_CHECKING

import asyncio

from shimoku.api.base_resource import Resource, ResourceCache
from shimoku.api.resources.role import (
    Role,
    create_role,
    get_role,
    get_roles,
    delete_role,
)
from shimoku.api.resources.app import App

from dataclasses import dataclass

if TYPE_CHECKING:
    from shimoku.api.resources.business import Business
from shimoku.exceptions import BoardError
import logging
from shimoku.execution_logger import log_error

logger = logging.getLogger(__name__)


class Dashboard(Resource):
    """Dashboard resource class"""

    resource_type = "dashboard"
    alias_field = "name"
    plural = "dashboards"

    class AppDashboard(Resource):
        """AppDashboard resource class"""

        resource_type = "appDashboard"
        plural = "appDashboards"

        def __init__(
            self,
            parent: "Dashboard",
            uuid: Optional[str] = None,
            app: App = None,
            db_resource: Optional[dict] = None,
        ):
            params = dict(
                appId=app["id"] if app else None,
            )
            super().__init__(
                parent=parent,
                uuid=uuid,
                db_resource=db_resource,
                check_params_before_creation=["appId"],
                params=params,
            )

        async def delete(self):
            """Deletes the appDashboard"""
            return await self._base_resource.delete()

    @dataclass
    class PublicPermission:
        """PublicPermission class"""

        isPublic: bool
        permission: str
        token: str

    def __init__(
        self,
        parent: "Business",
        uuid: Optional[str] = None,
        alias: Optional[str] = None,
        db_resource: Optional[dict] = None,
    ):
        params = dict(
            name=alias,
            order=0,
            isDisabled=False,
            theme={},
            publicPermission=self.PublicPermission(
                isPublic=False, permission="READ", token="default token"
            ),
        )

        super().__init__(
            parent=parent,
            uuid=uuid,
            db_resource=db_resource,
            children=[Dashboard.AppDashboard, Role],
            check_params_before_creation=["name"],
            params=params,
            params_to_serialize=["theme"],
        )

        self.currently_in_use = False

    async def delete(self):
        """Deletes the dashboard"""
        if self.currently_in_use:
            log_error(
                logger,
                f"Workspace {str(self)} is currently in use and cannot be deleted",
                BoardError,
            )
        return await self._base_resource.delete()

    async def update(self):
        """Updates the dashboard"""
        return await self._base_resource.update()

    async def list_app_ids(self) -> list[str]:
        """Returns the list of app ids in the dashboard"""
        cache: ResourceCache = self._base_resource.children[Dashboard.AppDashboard]
        cache_list = await cache.list()
        return list(set([app_dashboard["appId"] for app_dashboard in cache_list]))

    async def insert_app(self, app: App):
        """Inserts an app in the dashboard
        :param app: The App to insert
        """
        dashboards = await self._base_resource.parent.get_dashboards()
        app_ids_lists = await asyncio.gather(
            *[dashboard.list_app_ids() for dashboard in dashboards]
        )
        app_ids = [app_id for app_ids_list in app_ids_lists for app_id in app_ids_list]
        if app["id"] in app_ids:
            logger.warning(
                f"Menu path {str(app)} already exists in another board, it will appear in both boards"
            )
        await self._base_resource.create_child(Dashboard.AppDashboard, appId=app["id"])
        logger.info(f"Menu path {str(app)} added to board {str(self)}")

    async def remove_app(self, app: App):
        """Removes an app from the dashboard
        :param app: The App to remove
        """
        tasks = []
        cache: ResourceCache = self._base_resource.children[Dashboard.AppDashboard]
        cache_list = await cache.list()
        for app_dashboard in cache_list:
            if app_dashboard["appId"] == app["id"]:
                tasks.append(cache.delete(uuid=app_dashboard["id"]))

        await asyncio.gather(*tasks)
        logger.info(f"Menu path {str(app)} removed from board {str(self)}")

    async def remove_all_apps(self):
        """Removes all apps from the dashboard"""
        tasks = []
        cache: ResourceCache = self._base_resource.children[Dashboard.AppDashboard]
        cache_list = await cache.list()
        for app_dashboard in cache_list:
            tasks.append(cache.delete(uuid=app_dashboard["id"]))

        await asyncio.gather(*tasks)

    # Role methods
    get_role = get_role
    get_roles = get_roles
    create_role = create_role
    delete_role = delete_role
