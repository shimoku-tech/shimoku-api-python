import asyncio

from typing import Dict, Optional, List
from abc import ABC

from ..async_execution_pool import async_auto_call_manager, ExecutionPoolContext
from ..resources.role import user_delete_role, user_get_role, user_get_roles, user_create_role
from ..resources.universe import Universe
from ..resources.business import Business

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class BusinessMetadataApi(ABC):
    """
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, universe: 'Universe', execution_pool_context: ExecutionPoolContext):
        self._universe = universe
        self.epc = execution_pool_context

        self._get_for_roles = self._get_business_with_warning

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_business(self, name: str, create_default_roles: bool = True,
                              theme: Optional[Dict] = None) -> Dict:
        """Create a new business and the necessary roles if specified
        :param name: Name of the business
        :param create_default_roles: Create the default roles for the business
        :param theme: Theme of the business
        :return: Business data
        """
        business = await self._universe.create_business(name=name, theme=theme)

        if create_default_roles:
            create_roles_tasks = []

            for role_permission_resource in ['DATA', 'DATA_EXECUTION', 'USER_MANAGEMENT', 'BUSINESS_INFO']:
                create_roles_tasks.append(
                    business.create_role(
                        role='business_read',
                        resource=role_permission_resource,
                    )
                )

            await asyncio.gather(*create_roles_tasks)

        return business.cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def update_business(self, uuid: Optional[str] = None, name: Optional[str] = None,
                              new_name: Optional[str] = None, theme: Optional[Dict] = None):
        """Update a business
        :param name: Name of the business
        :param uuid: UUID of the business
        :param new_name: New name of the business
        :param theme: New theme of the business
        """
        params = {}

        if new_name:
            params['new_name'] = new_name

        if isinstance(theme, dict):
            params['theme'] = theme

        return await self._universe.update_business(uuid=uuid, name=name, **params)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_business(self, uuid: Optional[str] = None, name: Optional[str] = None):
        """Delete a business
        :param name: Name of the business
        :param uuid: UUID of the business
        """
        return await self._universe.delete_business(uuid=uuid, name=name)

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_business_with_warning(self, uuid: Optional[str] = None, name: Optional[str] = None
                                         ) -> Optional[Business]:
        """ Get the business
        :param name: name of the business
        :param uuid: UUID of the business
        """
        business: Business = await self._universe.get_business(uuid=uuid, name=name)
        if not business:
            logger.warning(f"Business with {name if name else uuid} not found")
        return business

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_business(self, uuid: Optional[str] = None, name: Optional[str] = None) -> Dict:
        """Get a business
        :param name: Name of the business
        :param uuid: UUID of the business
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return {}
        return business.cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_business_apps(self, uuid: Optional[str] = None, name: Optional[str] = None) -> List[Dict]:
        """Get the apps of a business
        :param name: Name of the business
        :param uuid: UUID of the business
        :return: List of apps
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return []
        return [app.cascade_to_dict() for app in await business.get_apps()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_business_app_ids(self, uuid: Optional[str] = None, name: Optional[str] = None) -> List[Dict]:
        """Get the apps of a business
        :param name: Name of the business
        :param uuid: UUID of the business
        :return: List of app ids
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return []
        return [app['id'] for app in await business.get_apps()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_business_dashboards(self, uuid: Optional[str] = None, name: Optional[str] = None) -> List[Dict]:
        """Get the apps of a business
        :param name: Name of the business
        :param uuid: UUID of the business
        :return: List of dashboards
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return []
        return [dashboard.cascade_to_dict() for dashboard in await business.get_dashboards()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_business_apps(self, uuid: Optional[str] = None, name: Optional[str] = None):
        """Delete all apps of a business
        :param name: Name of the business
        :param uuid: UUID of the business
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return
        apps = await business.get_apps()
        await asyncio.gather(*[business.delete_app(uuid=app['id']) for app in apps])

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_business_dashboards(self, uuid: Optional[str] = None, name: Optional[str] = None):
        """Delete all dashboards of a business
        :param name: Name of the business
        :param uuid: UUID of the business
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return
        dashboards = await business.get_dashboards()
        await asyncio.gather(*[business.delete_dashboard(uuid=dashboard['id']) for dashboard in dashboards])

    # Role management
    get_role = user_get_role
    get_roles = user_get_roles
    create_role = user_create_role
    delete_role = user_delete_role
