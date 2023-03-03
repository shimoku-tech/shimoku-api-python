""""""
import json
from typing import Dict, Tuple, Optional
from abc import ABC

from shimoku_api_python.api.explorer_api import DashboardExplorerApi
from shimoku_api_python.api.business_metadata_api import BusinessMetadataApi
from shimoku_api_python.async_execution_pool import async_auto_call_manager
import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


class DashboardMetadataApi(ABC):
    """
    DashboardMetadataApi is a class that contains all the methods to interact with the dashboard metadata in the API
    """

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, business_metadata_api: BusinessMetadataApi, **kwargs):
        self._dashboard_explorer_api = DashboardExplorerApi(api_client)
        self._business_metadata_api = business_metadata_api

        self._dashboard_id_by_name = {}

        self.business_id = None
        if kwargs.get('business_id'):
            self.business_id = kwargs.get('business_id')

    @staticmethod
    @logging_before_and_after(logging_level=logger.debug)
    def _create_normalized_name(name: str) -> str:
        """Having a name create a normalizedName

        Example
        ----------------------
        # "name": "   Test Borrar_grafico    "
        # "normalizedName": "test-borrar-grafico"
        """
        # remove empty spaces at the beginning and end
        name: str = name.strip()
        # replace "_" for www protocol it is not good
        name = name.replace('_', '-')

        return '-'.join(name.split(' ')).lower()

    @logging_before_and_after(logging_level=logger.debug)
    async def _resolve_dashboard_id(self, dashboard_id: Optional[str] = None,
                                    dashboard_name: Optional[str] = None) -> Optional[str]:
        """
        Resolve the app id from the app id or the menu path.
        :param dashboard_id: UUID of the dashboard
        :param dashboard_name: name of the dashboard
        :return: UUID of the dashboard
        """
        if dashboard_id:
            return dashboard_id

        if not dashboard_name:
            log_error(logger, 'Either the dashboard id or the dashboard name must be provided', ValueError)

        if dashboard_name not in self._dashboard_id_by_name:
            if not self.business_id:
                log_error(logger, 'The business has not been set', ValueError)

            self._dashboard_id_by_name = {}
            dashboards = await self._dashboard_explorer_api.get_business_dashboards(self.business_id)
            for dashboard in dashboards:
                self._dashboard_id_by_name[dashboard['name']] = dashboard['id']

            if dashboard_name not in self._dashboard_id_by_name:
                return None

        return self._dashboard_id_by_name[dashboard_name]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def set_business(self, business_id: str):
        """"""
        # If the business id does not exist it raises an ApiClientError
        _ = await self._business_metadata_api.get_business(business_id)
        self.business_id: str = business_id

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_dashboard(self, name: str, order: int, public_permission: Dict = None,
                               is_disabled: bool = False):
        """"""

        public_permission = public_permission or {}

        if not self.business_id:
            log_error(logger, 'The business id has not been set', ValueError)

        if await self._resolve_dashboard_id(dashboard_name=name):
            logger.warning(f'The dashboard {name} already exists in the business {self.business_id}, '
                           f'not doing anything')
            return None

        dashboard_metadata = {
            'name': name,
            'normalizedName': self._create_normalized_name(name),
            'order': order,
            # 'publicPermission': public_permission,
            'isDisabled': is_disabled
        }

        return await self._dashboard_explorer_api.create_dashboard(self.business_id, dashboard_metadata)

    @logging_before_and_after(logging_level=logger.debug)
    async def _async_get_dashboard(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None):
        """ Get the dashboard metadata
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        :return: dashboard metadata
        """

        dashboard_id = await self._resolve_dashboard_id(dashboard_id, dashboard_name)

        if not dashboard_id:
            return None

        return await self._dashboard_explorer_api.get_dashboard(self.business_id, dashboard_id)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_dashboard(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None) -> Optional[Dict]:
        """ Get the dashboard metadata
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        :return: dashboard metadata
        """
        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id)

        if not dashboard:
            logger.warning(f'There is no dashboard with the name {dashboard_name} '
                           f'in the business {self.business_id}, returning None')
            return None

        return dashboard

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_dashboard(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None):
        """
        Delete a dashboard
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        """
        dashboard_id = await self._resolve_dashboard_id(dashboard_id, dashboard_name)
        while dashboard_id:

            await self._dashboard_explorer_api.delete_dashboard(self.business_id, dashboard_id)
            del self._dashboard_id_by_name[dashboard_name]
            dashboard_id = None

            if dashboard_name:
                dashboard_id = await self._resolve_dashboard_id(dashboard_name=dashboard_name)
                if dashboard_id:
                    logger.info(f'There is another dashboard with the name {dashboard_name}, deleting it...')

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def update_dashboard(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None,
                               name: Optional[str] = None, order: Optional[int] = None,
                               public_permission: Optional[Dict] = None, is_disabled: Optional[bool] = None):
        """"""

        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id)

        if not dashboard:
            logger.warning(f'There is no dashboard with the name {dashboard_name} in the business {self.business_id}, '
                           f'not doing anything')
            return None

        dashboard_id = dashboard['id']
        dashboard_name = dashboard['name']

        dashboard_metadata = {}

        if name:
            dashboard_metadata['name'] = name
            dashboard_metadata['normalizedName'] = self._create_normalized_name(name)

        if order is not None:
            dashboard_metadata['order'] = order

        if public_permission is not None:
            dashboard_metadata['publicPermission'] = public_permission

        if is_disabled is not None:
            dashboard_metadata['isDisabled'] = is_disabled

        await self._dashboard_explorer_api.update_dashboard(self.business_id, dashboard_id, dashboard_metadata)

        if name:
            self._dashboard_id_by_name[name] = dashboard_id
            del self._dashboard_id_by_name[dashboard_name]




