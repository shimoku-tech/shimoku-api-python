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

    def get_app_by_type(
        self, business_id: str, app_type: str,
    ) -> Union[Dict, List[Dict]]:
        """Given a business retrieve all app metadata

        :param business_id: business UUID
        :param app_type:
        """
        endpoint: str = f'business/{business_id}/apps'
        app_ids: Dict = (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )

        # Is expected to be a single item (Dict) but an App
        # could have several reports with the same name
        result: Union[Dict, List[Dict]] = {}
        for app_id in app_ids:
            app: Dict = self.get_app(business_id=business_id, app_id=app_id)
            if app['appType'] == app_type:
                if result:
                    if len(result) == 1:
                        result: List[Dict] = [result] + [app]
                    else:
                        result: List[Dict] = result + [app]
                else:
                    result: Dict = app
        return result

# TODO es name o title?
    def get_app_by_name(
        self, business_id: str, app_name: str
    ) -> Union[Dict, List[Dict]]:
        """Given a business retrieve all app metadata

        :param business_id: business UUID
        :param app_name:
        """
        endpoint: str = f'business/{business_id}/apps'
        app_ids: Dict = (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )

        # Is expected to be a single item (Dict) but an App
        # could have several reports with the same name
        result: Union[Dict, List[Dict]] = {}
        for app_id in app_ids:
            app: Dict = self.get_app(business_id=business_id, app_id=app_id)
            if app['name'] == app_name:
                if result:
                    if len(result) == 1:
                        result: List[Dict] = [result] + [app]
                    else:
                        result: List[Dict] = result + [app]
                else:
                    result: Dict = app
        return result

    def rename_app(
        self, business_id: str, app_id: str, new_app_name: str,
    ) -> Dict:
        """Update path name
        """
        app_data = {'name': new_app_name}
        self.update_app(
            business_id=business_id,
            app_id=app_id,
            app_data=app_data,
        )

    def hide_title(
        self, business_id: str, app_id: str, hide_title: bool = True
    ) -> Dict:
        """Hide / show app title
        """
        app_data = {'hideTitle': hide_title}
        self.update_app(
            business_id=business_id,
            app_id=app_id,
            app_data=app_data,
        )

    def show_title(self, business_id: str, app_id: str) -> Dict:
        return self.hide_title(
            business_id=business_id,
            app_id=app_id,
            hide_title=False,
        )
