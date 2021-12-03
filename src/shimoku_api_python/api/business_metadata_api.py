""""""
from typing import Dict
from abc import ABC

from shimoku_api_python.api.explorer_api import BusinessExplorerApi


class BusinessMetadataApi(BusinessExplorerApi, ABC):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def copy_business(self):
        """Having a business make a copy of all its apps and reports
        for a new business (without data) so that the data could be filled next
        """
        raise NotImplementedError

    def rename_business(self, business_id: str, new_name: str) -> Dict:
        return self.update_business(
            business_id=business_id,
            business_data={'name': new_name}
        )
