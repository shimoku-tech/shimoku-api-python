""""""
import json
import asyncio

from typing import Dict, Callable
from abc import ABC

from shimoku_api_python.api.explorer_api import BusinessExplorerApi
from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext, \
    decorate_external_function
import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class BusinessMetadataApi(ABC):
    """
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, execution_pool_context: ExecutionPoolContext):
        self.business_explorer_api = BusinessExplorerApi(api_client)
        self.api_client = api_client
        self.epc = execution_pool_context

        self.async_get_business_activities = self.business_explorer_api.get_business_activities
        self.get_business_activities = decorate_external_function(self, self.business_explorer_api, 'get_business_activities')
        self.get_business = decorate_external_function(self, self.business_explorer_api, 'get_business')
        self.get_business_by_name = decorate_external_function(self, self.business_explorer_api, 'get_business_by_name')
        self.get_universe_businesses = decorate_external_function(self, self.business_explorer_api, 'get_universe_businesses')
        self.update_business = decorate_external_function(self, self.business_explorer_api, 'update_business')

        self.get_business_apps = decorate_external_function(self, self.business_explorer_api, 'get_business_apps')
        self.get_business_app_ids = decorate_external_function(self, self.business_explorer_api, 'get_business_app_ids')
        self.get_business_all_apps_with_filter = decorate_external_function(self, self.business_explorer_api, 'get_business_all_apps_with_filter')

        self.get_business_reports = decorate_external_function(self, self.business_explorer_api, 'get_business_reports')
        self.get_business_report_ids = decorate_external_function(self, self.business_explorer_api, 'get_business_report_ids')

        self.delete_business = decorate_external_function(self, self.business_explorer_api, 'delete_business')

        self.create_role = decorate_external_function(self, self.business_explorer_api, 'create_role')
        self.get_roles = decorate_external_function(self, self.business_explorer_api, 'get_roles')
        self.get_roles_by_name = decorate_external_function(self, self.business_explorer_api, 'get_roles_by_name')
        self.delete_role = decorate_external_function(self, self.business_explorer_api, 'delete_role')

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.debug)
    async def create_business(self, name: str, create_default_roles: bool = True) -> Dict:
        """Create a new business and the necessary roles if specified
        :param name: Name of the business
        :param create_default_roles: Create the default roles for the business
        :return: Business data
        """
        business_data = await self.business_explorer_api.create_business(name)

        if create_default_roles:
            create_roles_tasks = []

            for role_permisson_resource in ['DATA', 'DATA_EXECUTION', 'USER_MANAGEMENT', 'BUSINESS_INFO']:
                create_roles_tasks.append(
                    self.business_explorer_api.create_role(
                        business_id=business_data['id'],
                        role_name='business_read',
                        resource=role_permisson_resource,
                    )
                )

            await asyncio.gather(*create_roles_tasks)

        return business_data

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
