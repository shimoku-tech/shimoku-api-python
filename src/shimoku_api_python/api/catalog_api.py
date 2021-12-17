""""""

from typing import Dict

from .explorer_api import MultiCascadeExplorerAPI


class CatalogExplorerApi(MultiCascadeExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)

    def create_catalog_demo(self, owner_id: str) -> Dict[str, str]:
        """A single command to create a whole catalog
        """
        raise NotImplementedError

    def cohort(self):
        raise NotImplementedError
