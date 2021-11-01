""""""

from typing import Dict

from .explorer_api import MultiCascadeExplorerAPI


class CatalogExplorerApi(MultiCascadeExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)

    # TODO WiP
    def create_catalog_demo(self, owner_id: str) -> Dict[str, str]:
        """A single command to create a whole catalog
        """
        # TODO pending all the metadata to create a business
        result = self.create_business(owner_id)
        # TODO to validate this
        business_id: str = result.content['data']['businessId']

        # TODO pending all the metadata to create an app
        result = self.create_app(business_id)
        # TODO to validate this
        app_id: str = result.content['data']['appId']

        # TODO pending all the metadata to create a report
        result = self.create_report(app_id)
        # TODO to validate this
        report_id: str = result.content['data']['reportId']

        return {
            'business_id': business_id,
            'app_id': app_id,
            'report_id': report_id,
        }

    # TODO WiP
    def create_business_demo(self, owner_id: str) -> Dict[str, str]:
        """A single command to first create something
        """
        # TODO pending all the metadata to create a business
        result = self.create_business(owner_id)
        # TODO to validate this
        business_id: str = result.content['data']['businessId']

        # TODO pending all the metadata to create an app
        result = self.create_app(business_id)
        # TODO to validate this
        app_id: str = result.content['data']['appId']

        # TODO pending all the metadata to create a report
        result = self.create_report(app_id)
        # TODO to validate this
        report_id: str = result.content['data']['reportId']

        return {
            'business_id': business_id,
            'app_id': app_id,
            'report_id': report_id,
        }

    # TODO WiP
    def create_app_demo(self, business_id: str) -> Dict[str, str]:
        """A single command to first create something
        """
        # TODO pending all the metadata to create an app
        result = self.create_app(business_id)
        # TODO to validate this
        app_id: str = result.content['data']['appId']

        # TODO pending all the metadata to create a report
        result = self.create_report(app_id)
        # TODO to validate this
        report_id: str = result.content['data']['reportId']

        return {
            'business_id': business_id,
            'app_id': app_id,
            'report_id': report_id,
        }
