from uuid import uuid1
from typing import Optional, List, TYPE_CHECKING

from ..base_resource import Resource
from ..utils import clean_menu_path
from .role import Role, create_role, get_role, get_roles, delete_role
from .dashboard import Dashboard
from .app import App

if TYPE_CHECKING:
    from .universe import Universe

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class Business(Resource):

    resource_type = 'business'
    alias_field = 'name'
    plural = 'businesses'

    @logging_before_and_after(logger.debug)
    def __init__(self, parent: 'Universe', uuid: Optional[str] = None, alias: Optional[str] = None):

        params = {
            'name': alias,
            'theme': {},
        }

        super().__init__(parent=parent, uuid=uuid, children=[Dashboard, App, Role],
                         check_params_before_creation=['name'], params_to_serialize=['theme'],
                         params=params)

    @logging_before_and_after(logger.debug)
    async def delete(self):
        return await self._base_resource.delete()

    @logging_before_and_after(logger.debug)
    async def update(self):
        return await self._base_resource.update()

    # Dashboard methods
    @logging_before_and_after(logger.debug)
    async def create_dashboard(self, name: str, order: int, is_public: bool = False, is_disabled: bool = False
                               ) -> Dashboard:
        dashboard_metadata = dict(
            order=order,
            isDisabled=is_disabled
        )
        if is_public:
            dashboard_metadata['publicPermission'] = dict(
                isPublic=True,
                permission='READ',
                token=str(uuid1())
            )
        dashboard = await self._base_resource.create_child(Dashboard, alias=name, **dashboard_metadata)
        logger.info(f'Dashboard {name} created with id {dashboard["id"]}')
        return dashboard

    @logging_before_and_after(logger.debug)
    async def update_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None, **params):
        if 'new_name' in params:
            params['new_alias'] = params.pop('new_name')
        return await self._base_resource.update_child(Dashboard, uuid=uuid, alias=name, **params)

    @logging_before_and_after(logger.debug)
    async def get_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None,
                            create_if_not_exists: bool = True) -> Optional[Dashboard]:
        dashboard = await self._base_resource.get_child(Dashboard, uuid, name, create_if_not_exists)

        if dashboard:
            logger.info(f'Retrieved dashboard {dashboard["name"]} with id {dashboard["id"]}')

        return dashboard

    @logging_before_and_after(logger.debug)
    async def get_dashboards(self) -> List[Dashboard]:
        return await self._base_resource.get_children(Dashboard)

    @logging_before_and_after(logger.debug)
    async def delete_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None) -> Dashboard:
        return await self._base_resource.delete_child(Dashboard, uuid, name)

    # App methods
    @logging_before_and_after(logger.debug)
    async def get_app(self, uuid: Optional[str] = None, menu_path: Optional[str] = None,
                      create_if_not_exists: bool = True) -> Optional[App]:

        name = None
        if menu_path:
            name, _ = clean_menu_path(menu_path=menu_path)

        app = await self._base_resource.get_child(App, uuid, name, create_if_not_exists)

        if app:
            logger.info(f'Retrieved app {app["name"]} with id {app["id"]}')

        return app

    @logging_before_and_after(logger.debug)
    async def get_apps(self) -> List[App]:
        return await self._base_resource.get_children(App)

    @logging_before_and_after(logger.debug)
    async def delete_app(self, uuid: Optional[str] = None, menu_path: Optional[str] = None):

        name = None
        if menu_path:
            name, _ = clean_menu_path(menu_path=menu_path)

        return await self._base_resource.delete_child(App, uuid, name)

    @logging_before_and_after(logger.debug)
    async def update_app(self, uuid: Optional[str] = None, menu_path: Optional[str] = None, **params):

        if 'new_name' in params:
            params['new_alias'] = params.pop('new_name')

        name = None
        if menu_path:
            name, _ = clean_menu_path(menu_path=menu_path)

        return await self._base_resource.update_child(App, uuid=uuid, alias=name, **params)

    # Role methods
    get_role = get_role
    get_roles = get_roles
    create_role = create_role
    delete_role = delete_role
