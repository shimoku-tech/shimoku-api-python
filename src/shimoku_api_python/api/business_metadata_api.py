""""""
import json
from typing import Dict
from abc import ABC

from shimoku_api_python.api.explorer_api import BusinessExplorerApi
from shimoku_api_python.async_execution_pool import async_auto_call_manager
import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class BusinessMetadataApi(BusinessExplorerApi, ABC):
    """
    """
    get_business = async_auto_call_manager(execute=True)(BusinessExplorerApi.get_business)
    get_universe_businesses = async_auto_call_manager(execute=True)(BusinessExplorerApi.get_universe_businesses)
    create_business = async_auto_call_manager(execute=True)(BusinessExplorerApi.create_business)
    update_business = async_auto_call_manager(execute=True)(BusinessExplorerApi.update_business)

    get_business_apps = async_auto_call_manager(execute=True)(BusinessExplorerApi.get_business_apps)
    get_business_app_ids = async_auto_call_manager(execute=True)(BusinessExplorerApi.get_business_app_ids)
    get_business_all_apps_with_filter = async_auto_call_manager(execute=True)(BusinessExplorerApi.get_business_all_apps_with_filter)

    get_business_reports = async_auto_call_manager(execute=True)(BusinessExplorerApi.get_business_reports)
    get_business_report_ids = async_auto_call_manager(execute=True)(BusinessExplorerApi.get_business_report_ids)

    delete_business = async_auto_call_manager(execute=True)(BusinessExplorerApi.delete_business)
    
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client):
        self.api_client = api_client

    @logging_before_and_after(logging_level=logger.debug)
    def copy_business(self):
        """Having a business make a copy of all its apps and reports
        for a new business (without data) so that the data could be filled next
        """
        raise NotImplementedError

    @logging_before_and_after(logging_level=logger.info)
    def rename_business(self, business_id: str, new_name: str) -> Dict:
        return self.update_business(
            business_id=business_id,
            business_data={'name': new_name}
        )

    @logging_before_and_after(logging_level=logger.info)
    def update_business_theme(self, business_id: str, theme: Dict):
        return self.update_business(
            business_id=business_id,
            business_data={'theme': json.dumps(theme)}
        )
