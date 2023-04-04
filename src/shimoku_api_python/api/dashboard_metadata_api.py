""""""
import json
from typing import Dict, Tuple, Optional, List
from abc import ABC

import asyncio

from shimoku_api_python.api.explorer_api import DashboardExplorerApi
from shimoku_api_python.api.business_metadata_api import BusinessMetadataApi
from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext
import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


class DashboardMetadataApi(ABC):
    """
    DashboardMetadataApi is a class that contains all the methods to interact with the dashboard metadata in the API
    """

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, business_metadata_api: BusinessMetadataApi,
                 execution_pool_context: ExecutionPoolContext, **kwargs):
        self._dashboard_explorer_api = DashboardExplorerApi(api_client)
        self._business_metadata_api = business_metadata_api
        self.epc = execution_pool_context

        self._dashboard_id_by_name = {}

        self.business_id = None
        if kwargs.get('business_id'):
            self.business_id = kwargs.get('business_id')

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

    @logging_before_and_after(logging_level=logger.info)
    def set_business(self, business_id: str):
        """"""
        # If the business id does not exist it raises an ApiClientError
        self._business_metadata_api.get_business(business_id)
        self.business_id: str = business_id

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_dashboard(self, dashboard_name: str, order: Optional[int] = None, public_permission: Optional[Dict] = None,
                               is_disabled: bool = False):
        """"""
        result = await self._async_create_dashboard(dashboard_name, order, public_permission, is_disabled)

        if result is None:
            logger.warning(f'The dashboard {dashboard_name} already exists in the business {self.business_id}, '
                           f'not doing anything')

        return result

    @logging_before_and_after(logging_level=logger.debug)
    async def _async_create_dashboard(self, dashboard_name: str, order: Optional[int] = None,
                                      public_permission: Optional[str] = None, is_disabled: Optional[bool] = False):
        """"""

        if not self.business_id:
            log_error(logger, 'The business id has not been set', ValueError)

        if await self._resolve_dashboard_id(dashboard_name=dashboard_name):
            return None

        dashboard_metadata = {
            'name': dashboard_name,
            'order': order or len(self._dashboard_id_by_name),
            'isDisabled': is_disabled
        }
        if public_permission:
            dashboard_metadata['publicPermission'] = json.dumps({
                'isPublic': True,
                'permission': 'READ',
                'token': public_permission
            })

        result = await self._dashboard_explorer_api.create_dashboard(self.business_id, dashboard_metadata)
        self._dashboard_id_by_name[dashboard_name] = result['id']

        return result

    @logging_before_and_after(logging_level=logger.debug)
    async def _async_get_dashboard(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None,
                                   warn: bool = False):
        """ Get the dashboard metadata
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        :return: dashboard metadata
        """

        dashboard_id = await self._resolve_dashboard_id(dashboard_id, dashboard_name)

        if not dashboard_id:
            if warn:
                logger.warning(
                    f'There is no dashboard with the name {dashboard_name} in the business {self.business_id}, '
                    f'not doing anything')
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

        return await self._async_get_dashboard(dashboard_name, dashboard_id, warn=True)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_dashboard(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None):
        """
        Delete a dashboard
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        """
        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id, warn=True)
        if not dashboard:
            return
        dashboard_id, dashboard_name = dashboard['id'], dashboard['name']

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
                               public_permission: Optional[str] = None, is_disabled: Optional[bool] = None):
        """"""

        if name in self._dashboard_id_by_name:
            logger.warning(f'The dashboard {name} already exists in the business {self.business_id}, '
                           f'not doing anything')
            return None

        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id, warn=True)

        if not dashboard:
            return None

        dashboard_id = dashboard['id']
        dashboard_name = dashboard['name']

        dashboard_metadata = {}

        if name:
            dashboard_metadata['name'] = name

        if order is not None:
            dashboard_metadata['order'] = order

        if public_permission is not None:
            dashboard_metadata['publicPermission'] = json.dumps({
                'isPublic': True,
                'permission': 'READ',
                'token': public_permission
            })

        if is_disabled is not None:
            dashboard_metadata['isDisabled'] = is_disabled

        await self._dashboard_explorer_api.update_dashboard(self.business_id, dashboard_id, dashboard_metadata)

        if name:
            self._dashboard_id_by_name[name] = dashboard_id
            del self._dashboard_id_by_name[dashboard_name]

    @logging_before_and_after(logging_level=logger.debug)
    async def _async_add_app_in_dashboard(self, app_id: str, dashboard_name: Optional[str] = None,
                                          dashboard_id: Optional[str] = None):
        """"""

        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id, warn=True)

        if not dashboard:
            return None

        dashboard_id = dashboard['id']

        await self._dashboard_explorer_api.add_app_in_dashboard(self.business_id, dashboard_id, app_id)

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def add_app_in_dashboard(self, app_id: str, dashboard_name: Optional[str] = None,
                                   dashboard_id: Optional[str] = None):
        """"""
        await self._async_add_app_in_dashboard(app_id, dashboard_name, dashboard_id)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_dashboards(self) -> List[Dict]:
        """ Get the list of dashboards
        :return: list of dashboards in the business
        """

        self._dashboard_id_by_name = {}

        dashboards = await self._dashboard_explorer_api.get_business_dashboards(self.business_id)
        for dashboard in dashboards:
            self._dashboard_id_by_name[dashboard['name']] = dashboard['id']

        return dashboards

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_dashboard_app_ids(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None) \
            -> List[str]:
        """ Get the list of the ids of the apps in the dashboard
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        :return: list of the ids of the apps in the dashboard
        """
        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id, warn=True)

        if not dashboard:
            return []

        return [app_dashboard_link['appId'] for app_dashboard_link
                in await self._dashboard_explorer_api.app_dashboard_links(business_id=self.business_id,
                                                                          dashboard_id=dashboard['id'])]

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def remove_app_from_dashboard(self, app_id: str, dashboard_name: Optional[str] = None,
                                        dashboard_id: Optional[str] = None):
        """ Remove an app from a dashboard
        :param app_id: id of the app to remove
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        """
        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id, warn=True)

        app_dashboard_links = await self._dashboard_explorer_api.app_dashboard_links(business_id=self.business_id,
                                                                                     dashboard_id=dashboard['id'])

        app_dashboard_link_id = [app_dashboard_link['id'] for app_dashboard_link in app_dashboard_links
                                 if app_dashboard_link['appId'] == app_id][0]

        await self._dashboard_explorer_api.delete_app_dashboard_link(business_id=self.business_id,
                                                                     dashboard_id=dashboard['id'],
                                                                     app_dashboard_id=app_dashboard_link_id)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_role(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None,
                          resource: Optional[str] = None, role_name: Optional[str] = None,
                          permission: Optional[str] = None, target: Optional[str] = None)-> Dict:
        """ Create a role for a dashboard
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        :param resource: resources level of permission of the role
        :param role_name: role name
        :param permission: permission level of the role
        :param target: target of the role
        """
        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id, warn=True)

        if not dashboard:
            return {}

        return await self._dashboard_explorer_api.create_role(
            business_id=self.business_id, dashboard_id=dashboard['id'],
            resource=resource, role_name=role_name, permission=permission, target=target)

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def delete_role(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None,
                          role_id: Optional[str] = None):
        """ Delete a role of a dashboard
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        :param role_id: UUID of the role to delete
        """

        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id, warn=True)

        if not dashboard:
            return {}

        await self._dashboard_explorer_api.delete_role(business_id=self.business_id, dashboard_id=dashboard['id'],
                                                       role_id=role_id)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_roles(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None) -> List[Dict]:
        """ Get the list of roles of a dashboard
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        :return: list of roles of the dashboard
        """

        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id, warn=True)

        if not dashboard:
            return []

        return await self._dashboard_explorer_api.get_roles(business_id=self.business_id, dashboard_id=dashboard['id'])

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_roles_by_name(self, dashboard_name: Optional[str] = None, dashboard_id: Optional[str] = None,
                                role_name: Optional[str] = None) -> List[Dict]:
        """ Get the list of roles of a dashboard by name
        :param dashboard_name: name of the dashboard
        :param dashboard_id: UUID of the dashboard
        :param role_name: name of the role
        :return: list of roles of the dashboard
        """

        dashboard = await self._async_get_dashboard(dashboard_name, dashboard_id, warn=True)

        if not dashboard:
            return []

        return await self._dashboard_explorer_api.get_roles_by_name(business_id=self.business_id,
                                                                    dashboard_id=dashboard['id'], role_name=role_name)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_business_dashboards(self):
        """ Delete all dashboards of the business
        """
        dashboards = await self._dashboard_explorer_api.get_business_dashboards(business_id=self.business_id)

        delete_dashboard_tasks = []
        for dashboard in dashboards:
            delete_dashboard_tasks.append(
                self._dashboard_explorer_api.delete_dashboard(
                    business_id=self.business_id, dashboard_id=dashboard['id']
                )
            )

        await asyncio.gather(*delete_dashboard_tasks)
