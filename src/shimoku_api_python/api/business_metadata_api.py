import asyncio

from typing import Dict, Optional, List, Tuple
from abc import ABC

from ..async_execution_pool import async_auto_call_manager, ExecutionPoolContext
from ..resources.role import user_delete_role, user_get_role, user_get_roles, user_create_role
from ..resources.universe import Universe
from ..resources.business import Business
from ..resources.app import App
from ..resources.report import Report
from ..utils import create_normalized_name
from ..exceptions import WorkspaceError

import logging
from ..execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


class BusinessMetadataApi(ABC):
    """
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, universe: 'Universe', execution_pool_context: ExecutionPoolContext):
        self._universe = universe
        self.epc = execution_pool_context

        self._get_for_roles = self._get_business_with_warning

    async def _check_similar_name(self, name: str):
        """ Check if there exists a workspace with a very similar name
        :param name: Name of the workspace """
        all_business = await self._universe.get_businesses()
        normalized_name = create_normalized_name(name)
        if normalized_name in [create_normalized_name(business['name']) for business in all_business]:
            raise log_error(logger, 'There exists a workspace with a very similar name, please choose another name',
                            WorkspaceError)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_workspace(
        self, name: str, create_default_roles: bool = True,
        theme: Optional[Dict] = None
    ) -> Dict:
        """Create a new workspace and the necessary roles if specified
        :param name: Name of the workspace
        :param create_default_roles: Create the default roles for the workspace
        :param theme: Theme of the workspace
        :return: workspace data
        """
        await self._check_similar_name(name)

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
    async def update_workspace(
        self, uuid: Optional[str] = None, name: Optional[str] = None,
        new_name: Optional[str] = None, theme: Optional[Dict] = None
    ):
        """Update a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param new_name: New name of the workspace
        :param theme: New theme of the workspace
        """
        params = {}

        if new_name is not None:
            await self._check_similar_name(new_name)
            params['new_name'] = new_name

        if isinstance(theme, dict):
            params['theme'] = theme

        return await self._universe.update_business(uuid=uuid, name=name, **params)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_workspace(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """Delete a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        """
        return await self._universe.delete_business(uuid=uuid, name=name)

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_business_with_warning(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> Optional[Business]:
        """ Get the business
        :param name: name of the business
        :param uuid: UUID of the business
        """
        business: Business = await self._universe.get_business(uuid=uuid, name=name)
        if not business:
            logger.warning(f"Workspace with {name if name else uuid} not found")
        return business

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_workspace(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> Dict:
        """Get a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return {}
        return business.cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_workspace_menu_paths(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> List[Dict]:
        """Get the menu paths of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: List of apps
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return []
        return [app.cascade_to_dict() for app in await business.get_apps()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_workspace_menu_path_ids(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> List[Dict]:
        """Get the menu path ids of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: List of app ids
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return []
        return [app['id'] for app in await business.get_apps()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_workspace_boards(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> List[Dict]:
        """Get the boards of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: List of dashboards
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return []
        return [dashboard.cascade_to_dict() for dashboard in await business.get_dashboards()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_workspace_menu_paths(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """Delete all menu paths of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return
        apps = await business.get_apps()
        await asyncio.gather(*[business.delete_app(uuid=app['id']) for app in apps])

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_all_workspace_boards(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """Delete all boards of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return
        dashboards = await business.get_dashboards()
        await asyncio.gather(*[business.delete_dashboard(uuid=dashboard['id']) for dashboard in dashboards])

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def change_boards_order(
        self, boards: List[str], uuid: Optional[str] = None, name: Optional[str] = None,
    ):
        """Change the order of the boards of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param boards: List of dashboard names
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return
        await asyncio.gather(*[business.update_dashboard(name=d_name, order=i+1) for i, d_name in enumerate(boards)])

    @logging_before_and_after(logging_level=logger.debug)
    async def _change_sub_paths_order(
        self, business: Business, menu_path: str, sub_paths: List[str]
    ):
        """Change the order of the sub paths of an app
        :param app: App object
        :param sub_paths: List of sub paths
        """
        app: App = await business.get_app(name=menu_path, create_if_not_exists=False)
        if not app:
            logger.warning(f"Menu path {menu_path} not found")
            return
        reports: List[Report] = await app.get_reports()
        sub_paths = [create_normalized_name(sub_path) for sub_path in sub_paths]
        non_referenced_reports = sorted(
            [report for report in reports if report['path'] is not None and
             create_normalized_name(report['path']) not in sub_paths],
            key=lambda x: x['pathOrder']
        )
        for report in non_referenced_reports:
            sub_path = report['path']
            if sub_path not in sub_paths:
                sub_paths.append(sub_path)

        tasks = []
        for i, sub_path in enumerate(sub_paths):
            _reports = [report for report in reports if (report['path'] is not None and
                        create_normalized_name(report['path']) == create_normalized_name(sub_path))]
            for report in _reports:
                tasks.append(app.update_report(uuid=report['id'], pathOrder=i))

        logger.info(f'Updating {len(reports)} components from menu path {str(app)}')

        await asyncio.gather(*tasks)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def change_menu_order(
        self, menu_order: List, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """Change the order of the menu of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param menu_order: List of menu names
        """
        business = await self._get_business_with_warning(uuid=uuid, name=name)
        if not business:
            return
        tasks = []
        for i, menu_option in enumerate(menu_order):
            menu_name = menu_option
            if isinstance(menu_option, Tuple):
                menu_name, sub_paths = menu_option
                tasks.append(self._change_sub_paths_order(business=business, menu_path=menu_name, sub_paths=sub_paths))
            tasks.append(business.update_app(name=menu_name, order=i))

        await asyncio.gather(*tasks)

    # Role management
    get_role = user_get_role
    get_roles = user_get_roles
    create_role = user_create_role
    delete_role = user_delete_role
