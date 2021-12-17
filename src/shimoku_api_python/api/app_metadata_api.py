""""""

from abc import ABC
from typing import List, Dict, Union

from shimoku_api_python.api.explorer_api import AppExplorerApi


class AppMetadataApi(AppExplorerApi, ABC):
    """
    """

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
