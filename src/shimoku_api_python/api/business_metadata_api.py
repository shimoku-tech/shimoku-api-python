""""""
import json
from typing import Dict
from abc import ABC

from shimoku_api_python.api.explorer_api import BusinessExplorerApi
from shimoku_api_python.async_execution_pool import async_auto_call_manager
import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class BusinessMetadataApi(ABC):
    """
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client):
        self.business_explorer_api = BusinessExplorerApi(api_client)

        self.api_client = api_client
        self.get_business_activities = async_auto_call_manager(execute=True)(self.business_explorer_api.get_business_activities)
        self.get_business = async_auto_call_manager(execute=True)(self.business_explorer_api.get_business)
        self.get_universe_businesses = async_auto_call_manager(execute=True)(self.business_explorer_api.get_universe_businesses)
        self.create_business = async_auto_call_manager(execute=True)(self.business_explorer_api.create_business)
        self.update_business = async_auto_call_manager(execute=True)(self.business_explorer_api.update_business)

        self.get_business_apps = async_auto_call_manager(execute=True)(self.business_explorer_api.get_business_apps)
        self.get_business_app_ids = async_auto_call_manager(execute=True)(self.business_explorer_api.get_business_app_ids)
        self.get_business_all_apps_with_filter = async_auto_call_manager(execute=True)(self.business_explorer_api.get_business_all_apps_with_filter)

        self.get_business_reports = async_auto_call_manager(execute=True)(self.business_explorer_api.get_business_reports)
        self.get_business_report_ids = async_auto_call_manager(execute=True)(self.business_explorer_api.get_business_report_ids)

        self.delete_business = async_auto_call_manager(execute=True)(self.business_explorer_api.delete_business)

    @async_auto_call_manager(execute=True)
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
