""""""

from abc import ABC
from typing import Dict, List

from shimoku_api_python.api.explorer_api import AppTypeExplorerApi


class AppTypeMetadataApi(AppTypeExplorerApi, ABC):
    """
    """
    def __init__(self, api_client):
        self.api_client = api_client

    def rename_app_type_by_old_name(self, old_name: str, new_name) -> Dict:
        # Get all app_types
        app_types: List[Dict] = self.get_universe_app_types()

        # Find your target app_type by its current name
        target_app_type: List[Dict] = [
            app_type
            for app_type in app_types
            if app_type['name'] == old_name
        ]

        try:
            assert len(target_app_type) == 1
        except AssertionError:
            if len(target_app_type) == 0:
                raise ValueError('The provided old name does not exists')
            else:
                raise ValueError(
                    'There are multiple app_type with the same name '
                    'Find manually your target app_type and use '
                    'rename_apps_types() instead'
                )

        return self.rename_apps_types(
            app_type_id=target_app_type[0]['id'],
            new_name=new_name,
        )

    def rename_apps_types(self, app_type_id: str, new_name: str) -> Dict:
        return self.update_app_type(
            app_type_id=app_type_id,
            app_type_metadata={'name': new_name}
        )

    def get_app_type_by_name(self, name: str) -> Dict:
        app_types: List[Dict] = self.get_universe_app_types()
        target_app_type: List[Dict] = [
            app_type
            for app_type in app_types
            if app_type['name'] == name
        ]

        if target_app_type:
            assert len(target_app_type) == 1
            return target_app_type[0]
        else:
            return {}
