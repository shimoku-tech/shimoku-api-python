""""""

from abc import ABC
from typing import List, Dict, Union

from shimoku_api_python.api.explorer_api import (
    AppExplorerApi, MultiCreateApi,
    CascadeExplorerAPI, CascadeCreateExplorerAPI,
)
from shimoku_api_python.exceptions import ApiClientError


class AppMetadataApi(AppExplorerApi, ABC):
    """
    """
    _create_app_type_and_app = MultiCreateApi.create_app_type_and_app
    # TODO this a prior is in AppExplorerApi why if I remove this line it does not work?
    _get_app_by_name = CascadeExplorerAPI.get_app_by_name
    _create_app = CascadeCreateExplorerAPI.create_app

    def __init__(self, api_client):
        self.api_client = api_client

    def has_app_report(self, business_id: str, app_id: str) -> bool:
        """"""
        reports: List[str] = (
            self.get_app_reports(
                business_id=business_id,
                app_id=app_id,
            )
        )
        if reports:
            return True
        else:
            return False

    def hide_title(
        self, business_id: str, app_id: str, hide_title: bool = True
    ) -> Dict:
        """Hide / show app title
        """
        app_data = {'hideTitle': hide_title}
        return (
            self.update_app(
                business_id=business_id,
                app_id=app_id,
                app_data=app_data,
            )
        )

    def show_title(self, business_id: str, app_id: str) -> Dict:
        return self.hide_title(
            business_id=business_id,
            app_id=app_id,
            hide_title=False,
        )

    def get_or_create_app_and_apptype(self, business_id: str, name: str) -> Dict:
        """Try to create an App and AppType if they exist instead retrieve them"""
        try:
            d: Dict[str, Dict] = self._create_app_type_and_app(
                business_id=business_id,
                app_type_metadata={'name': name},
                app_metadata={},
            )
            app: Dict = d['app']
        except ApiClientError:  # Business admin user
            app: Dict = self._get_app_by_name(business_id=business_id, name=name)
            if not app:
                app: Dict = self._create_app(
                    business_id=business_id, name=name,
                )
        return app
