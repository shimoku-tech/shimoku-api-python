""""""

from abc import ABC
from typing import List, Dict, Optional

from shimoku_api_python.api.explorer_api import (
    AppExplorerApi, MultiCreateApi,
    CascadeExplorerAPI, CascadeCreateExplorerAPI,
    BusinessExplorerApi
)
from shimoku_api_python.exceptions import ApiClientError

from shimoku_api_python.async_execution_pool import async_auto_call_manager

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class AppMetadataApi(ABC):
    """
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, **kwargs):

        self.app_explorer_api = AppExplorerApi(api_client)
        self.business_explorer_api = BusinessExplorerApi(api_client)
        self.multi_create = MultiCreateApi(api_client)

        self._create_app_type_and_app = self.multi_create.create_app_type_and_app
        self._get_app_by_name = self.app_explorer_api.get_app_by_name
        self._create_app = self.app_explorer_api.create_app
        self._get_business = self.business_explorer_api.get_business

        self.get_app = async_auto_call_manager(execute=True)(self.app_explorer_api.get_app)
        self.create_app = async_auto_call_manager(execute=True)(self.app_explorer_api.create_app)
        self.update_app = async_auto_call_manager(execute=True)(self.app_explorer_api.update_app)

        self.get_business_apps = async_auto_call_manager(execute=True)(self.app_explorer_api.get_business_apps)
        self.find_app_by_name_filter = async_auto_call_manager(execute=True)(self.app_explorer_api.find_app_by_name_filter)
        self.get_app_reports = async_auto_call_manager(execute=True)(self.app_explorer_api.get_app_reports)
        self.get_app_report_ids = async_auto_call_manager(execute=True)(self.app_explorer_api.get_app_report_ids)
        self.get_app_path_names = async_auto_call_manager(execute=True)(self.app_explorer_api.get_app_path_names)
        self.get_app_reports_by_filter = async_auto_call_manager(execute=True)(self.app_explorer_api.get_app_reports_by_filter)
        self.get_app_by_type = async_auto_call_manager(execute=True)(self.app_explorer_api.get_app_by_type)
        self.get_app_type = async_auto_call_manager(execute=True)(self.app_explorer_api.get_app_type)
        self.get_app_by_name = async_auto_call_manager(execute=True)(self.app_explorer_api.get_app_by_name)

        self.delete_app = async_auto_call_manager(execute=True)(self.app_explorer_api.delete_app)

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
    async def get_or_create_app_and_apptype(self, name: str) -> Dict:
        """Try to create an App and AppType if they exist instead retrieve them"""
        # TODO investigate what to do with this
        # try:
        #     d: Dict[str, Dict] = await self._create_app_type_and_app(
        #         business_id=self.business_id,
        #         app_type_metadata={'name': name},
        #         app_metadata={},
        #     )
        #     app: Dict = d['app']
        # except ApiClientError:  # Business admin user
        app: Dict = await self._get_app_by_name(business_id=self.business_id, name=name)
        if not app:
            app: Dict = await self._create_app(
                business_id=self.business_id, name=name,
            )
        return app
