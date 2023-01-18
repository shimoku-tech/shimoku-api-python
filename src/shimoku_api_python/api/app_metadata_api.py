""""""

from abc import ABC
from typing import List, Dict, Optional

from shimoku_api_python.api.explorer_api import (
    AppExplorerApi, MultiCreateApi,
    CascadeExplorerAPI, CascadeCreateExplorerAPI,
    BusinessExplorerApi
)
from shimoku_api_python.exceptions import ApiClientError

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class AppMetadataApi(AppExplorerApi, ABC):
    """
    """
    _create_app_type_and_app = MultiCreateApi.create_app_type_and_app
    # TODO this a prior is in AppExplorerApi why if I remove this line it does not work?
    _get_app_by_name = CascadeExplorerAPI.get_app_by_name
    _create_app = CascadeCreateExplorerAPI.create_app
    _get_business = BusinessExplorerApi.get_business

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, **kwargs):
        self.api_client = api_client

        if kwargs.get('business_id'):
            self.business_id: Optional[str] = kwargs['business_id']
        else:
            self.business_id: Optional[str] = None

    @logging_before_and_after(logging_level=logger.debug)
    def set_business(self, business_id: str):
        """"""
        # If the business id does not exists it raises an ApiClientError
        _ = self._get_business(business_id)
        self.business_id: str = business_id

    @logging_before_and_after(logging_level=logger.debug)
    def __resolve_app_id(self, app_id: Optional[str] = None, app_name: Optional[str] = None) -> str:
        """"""
        if app_id:
            return app_id
        if not app_name:
            raise Exception("Either an app_id or an app_name has to be provided")

        return self._get_app_by_name(self.business_id, app_name)['id']

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
        try:
            d: Dict[str, Dict] = await self._create_app_type_and_app(
                business_id=self.business_id,
                app_type_metadata={'name': name},
                app_metadata={},
            )
            app: Dict = d['app']
        except ApiClientError:  # Business admin user
            app: Dict = await self._get_app_by_name(business_id=self.business_id, name=name)
            if not app:
                app: Dict = await self._create_app(
                    business_id=self.business_id, name=name,
                )
        return app
