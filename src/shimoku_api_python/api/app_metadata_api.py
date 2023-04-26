""""""

from abc import ABC
from typing import List, Dict, Optional, Callable
import asyncio

from shimoku_api_python.api.explorer_api import (
    AppExplorerApi, MultiCreateApi,
    CascadeExplorerAPI, CascadeCreateExplorerAPI,
    BusinessExplorerApi
)
from shimoku_api_python.api.dashboard_metadata_api import DashboardMetadataApi
from shimoku_api_python.exceptions import ApiClientError

from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext,\
    decorate_external_function

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class AppMetadataApi(ABC):
    """
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, dashboard_metadata_api: DashboardMetadataApi, execution_pool_context: ExecutionPoolContext, **kwargs):

        self._api_client = api_client
        self.dashboard_metadata_api = dashboard_metadata_api
        self.app_explorer_api = AppExplorerApi(api_client)
        self.business_explorer_api = BusinessExplorerApi(api_client)
        self.multi_create = MultiCreateApi(api_client)

        self._create_app_type_and_app = self.multi_create.create_app_type_and_app
        self._get_app_by_name = self.app_explorer_api.get_app_by_name
        self._create_app = self.app_explorer_api.create_app
        self._get_business = self.business_explorer_api.get_business
        self._add_app_in_dashboard = self.dashboard_metadata_api._async_add_app_in_dashboard
        self._is_app_in_dashboard = self.dashboard_metadata_api._async_is_app_in_dashboard
        self._create_dashboard = self.dashboard_metadata_api._async_create_dashboard

        self.get_app = decorate_external_function(self, self.app_explorer_api, 'get_app')
        self.create_app = decorate_external_function(self, self.app_explorer_api, 'create_app')
        self.update_app = decorate_external_function(self, self.app_explorer_api, 'update_app')
        self.delete_app = decorate_external_function(self, self.app_explorer_api, 'delete_app')

        self.get_business_apps = decorate_external_function(self, self.business_explorer_api, 'get_business_apps')
        self.find_app_by_name_filter = decorate_external_function(self, self.app_explorer_api, 'find_app_by_name_filter')
        self.get_app_reports = decorate_external_function(self, self.app_explorer_api, 'get_app_reports')
        self.get_app_report_ids = decorate_external_function(self, self.app_explorer_api, 'get_app_report_ids')
        self.get_app_path_names = decorate_external_function(self, self.app_explorer_api, 'get_app_path_names')
        self.get_app_reports_by_filter = decorate_external_function(self, self.app_explorer_api, 'get_app_reports_by_filter')
        self.get_app_by_type = decorate_external_function(self, self.app_explorer_api, 'get_app_by_type')
        self.get_app_type = decorate_external_function(self, self.app_explorer_api, 'get_app_type')
        self.get_app_by_name = decorate_external_function(self, self.app_explorer_api, 'get_app_by_name')

        self.create_role = decorate_external_function(self, self.app_explorer_api, 'create_role')
        self.get_roles = decorate_external_function(self, self.app_explorer_api, 'get_roles')
        self.get_roles_by_name = decorate_external_function(self, self.app_explorer_api, 'get_roles_by_name')
        self.delete_role = decorate_external_function(self, self.app_explorer_api, 'delete_role')

        self.epc = execution_pool_context

        self._apps = {}

        if kwargs.get('business_id'):
            self.business_id: Optional[str] = kwargs['business_id']
        else:
            self.business_id: Optional[str] = None

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.debug)
    async def set_business(self, business_id: str):
        """"""
        # If the business id does not exists it raises an ApiClientError
        _ = await self._get_business(business_id)
        self.business_id: str = business_id

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.debug)
    async def __resolve_app_id(self, app_id: Optional[str] = None, app_name: Optional[str] = None) -> str:
        """"""
        if app_id:
            return app_id
        if not app_name:
            raise Exception("Either an app_id or an app_name has to be provided")

        return (await self._get_app_by_name(self.business_id, app_name))['id']

    @logging_before_and_after(logging_level=logger.debug)
    def has_app_report(self, app_id: Optional[str] = None, app_name: Optional[str] = None) -> bool:
        """"""
        reports: List[str] = (
            self.get_app_reports(
                business_id=self.business_id,
                app_id=self.__resolve_app_id(app_id, app_name),
            )
        )
        if reports:
            return True
        else:
            return False

    @logging_before_and_after(logging_level=logger.info)
    def hide_title(
        self, app_id: Optional[str] = None, app_name: Optional[str] = None, hide_title: bool = True
    ) -> Dict:
        """Hide / show app title
        """
        app_data = {'hideTitle': hide_title}
        return (
            self.update_app(
                business_id=self.business_id,
                app_id=self.__resolve_app_id(app_id, app_name),
                app_metadata=app_data,
            )
        )

    @logging_before_and_after(logging_level=logger.info)
    def show_title(self, app_id: Optional[str] = None, app_name: Optional[str] = None) -> Dict:
        return self.hide_title(
            app_id=app_id,
            app_name=app_name,
            hide_title=False,
        )

    @logging_before_and_after(logging_level=logger.info)
    def hide_history_navigation(self, app_id: Optional[str] = None, app_name: Optional[str] = None) -> Dict:
        return (
            self.update_app(
                business_id=self.business_id,
                app_id=self.__resolve_app_id(app_id, app_name),
                app_metadata={'showHistoryNavigation': 'false'},
            )
        )

    @logging_before_and_after(logging_level=logger.info)
    def show_history_navigation(self, app_id: Optional[str] = None, app_name: Optional[str] = None) -> Dict:
        return (
            self.update_app(
                business_id=self.business_id,
                app_id=self.__resolve_app_id(app_id, app_name),
                app_metadata={'showHistoryNavigation': 'true'},
            )
        )

    @logging_before_and_after(logging_level=logger.info)
    def hide_breadcrumbs(self, app_id: Optional[str] = None, app_name: Optional[str] = None) -> Dict:
        return (
            self.update_app(
                business_id=self.business_id,
                app_id=self.__resolve_app_id(app_id, app_name),
                app_metadata={'showBreadcrumb': 'false'},
            )
        )

    @logging_before_and_after(logging_level=logger.info)
    def show_breadcrumbs(self, app_id: Optional[str] = None, app_name: Optional[str] = None) -> Dict:
        return (
            self.update_app(
                business_id=self.business_id,
                app_id=self.__resolve_app_id(app_id, app_name),
                app_metadata={'showBreadcrumb': 'true'},
            )
        )

    @logging_before_and_after(logging_level=logger.info)
    def hide_path(self, app_id: Optional[str] = None, app_name: Optional[str] = None) -> Dict:
        return (
            self.update_app(
                business_id=self.business_id,
                app_id=self.__resolve_app_id(app_id, app_name),
                app_metadata={'hidePath': 'true'},
            )
        )

    @logging_before_and_after(logging_level=logger.info)
    def show_path(self, app_id: Optional[str] = None, app_name: Optional[str] = None) -> Dict:
        return (
            self.update_app(
                business_id=self.business_id,
                app_id=self.__resolve_app_id(app_id, app_name),
                app_metadata={'hidePath': 'false'},
            )
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def _async_get_or_create_app_and_apptype(self, name: str, dashboard_name: Optional[str] = None) -> Dict:
        """Try to create an App and AppType if they exist instead retrieve them"""

        async with self._api_client.locks['get_create_app']:

            if name in self._apps:
                app: Dict = self._apps[name]
            else:
                app: Dict = await self._get_app_by_name(business_id=self.business_id, name=name)

            if not app:
                app: Dict = await self._create_app(
                    business_id=self.business_id, name=name,
                )
                logger.info(f'App {name} created with id {app["id"]}')

            if dashboard_name:
                await self._create_dashboard(dashboard_name=dashboard_name)
                if not await self._is_app_in_dashboard(app_id=app['id'], dashboard_name=dashboard_name):
                    await self._add_app_in_dashboard(app_id=app['id'], dashboard_name=dashboard_name)

            self._apps[name] = app

            return app

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_or_create_app_and_apptype(self, name: str, dashboard_name: Optional[str] = None) -> Dict:
        return await self._async_get_or_create_app_and_apptype(name=name, dashboard_name=dashboard_name)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_business_apps(self):
        """
        Deletes all the apps from the current business
        """
        tasks = []
        for app in await self.business_explorer_api.get_business_apps(self.business_id):
            tasks.append(self.app_explorer_api.delete_app(self.business_id, app['id']))
            logger.info(f'Deleting app {app["name"]} with id {app["id"]}')

        self._apps = {}

        await asyncio.gather(*tasks)
