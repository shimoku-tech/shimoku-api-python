from uuid import uuid1
from typing import Optional, List, Dict, TYPE_CHECKING

from ..base_resource import Resource
from ..websockets_server import EventType
from ..exceptions import WorkspaceError, MenuPathError, BoardError
from .role import Role, create_role, get_role, get_roles, delete_role
from .event import Event
from .dashboard import Dashboard
from .app import App

if TYPE_CHECKING:
    from .universe import Universe

import logging
from ..execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


class Business(Resource):

    resource_type = 'business'
    alias_field = 'name'
    plural = 'businesses'

    @logging_before_and_after(logger.debug)
    def __init__(self, parent: 'Universe', uuid: Optional[str] = None, alias: Optional[str] = None,
                 db_resource: Optional[Dict] = None):

        params = {
            'name': alias if alias else '',
            'theme': {},
        }

        super().__init__(parent=parent, uuid=uuid, db_resource=db_resource, children=[Dashboard, App, Role, Event],
                         check_params_before_creation=['name'], params_to_serialize=['theme'],
                         params=params)

        self.currently_in_use = False

    @logging_before_and_after(logger.debug)
    async def delete(self):
        if self.currently_in_use:
            log_error(logger, f'Workspace {str(self)} is currently in use and cannot be deleted', WorkspaceError)
        return await self._base_resource.delete()

    @logging_before_and_after(logger.debug)
    async def update(self):
        return await self._base_resource.update()

    # Event methods
    @logging_before_and_after(logger.debug)
    async def create_event(self, event_type: EventType, content: dict, resource_id: Optional[str] = None):
        """ Creates an event but dont store it in the cache
        :param event_type: The type of the event
        :param content: The content of the event
        :param resource_id: The id of the resource that triggered the event
        """
        if event_type != EventType.BUSINESS_CONTENTS_UPDATED:
            return

        event = Event(parent=self)
        event.set_params(type=event_type.value, content=content, resourceId=resource_id)
        await event

    # Dashboard methods
    @logging_before_and_after(logger.debug)
    async def create_dashboard(
        self, name: str, order: int, is_public: bool = False, is_disabled: bool = False
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
        logger.info(f'Board {name} created with id {dashboard["id"]}')
        return dashboard

    @logging_before_and_after(logger.debug)
    async def update_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None, **params):
        if params.get('new_name') is not None:
            params['name'] = params.pop('new_name')
            params['new_alias'] = True
        dashboard = await self.get_dashboard(uuid, name, create_if_not_exists=False)
        if not dashboard:
            logger.warning(f'Dashboard {name} not found, cannot update it')
            return
        await self._base_resource.update_child(Dashboard, uuid=uuid, alias=name, **params)
        await self.create_event(EventType.DASHBOARD_UPDATED, params, dashboard['id'])

    @logging_before_and_after(logger.debug)
    async def get_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None,
                            create_if_not_exists: bool = True) -> Optional[Dashboard]:
        dashboard = await self._base_resource.get_child(Dashboard, uuid, name)

        if dashboard:
            logger.info(f'Retrieved board {dashboard["name"]} with id {dashboard["id"]}')
        elif create_if_not_exists:
            if not name:
                log_error(logger, f'Name is required to create a board', BoardError)
            how_many_dashboards = len(await self.get_dashboards())
            dashboard = await self._base_resource.create_child(Dashboard, alias=name, order=how_many_dashboards + 1)
            logger.info(f'Created board {dashboard["name"]} with id {dashboard["id"]}')
            await self.create_event(EventType.DASHBOARD_CREATED, {}, dashboard['id'])

        return dashboard

    @logging_before_and_after(logger.debug)
    async def get_dashboards(self) -> List[Dashboard]:
        return await self._base_resource.get_children(Dashboard)

    @logging_before_and_after(logger.debug)
    async def delete_dashboard(self, uuid: Optional[str] = None, name: Optional[str] = None) -> bool:
        dashboard = await self.get_dashboard(uuid, name, create_if_not_exists=False)
        result = await self._base_resource.delete_child(Dashboard, uuid, name)
        await self.create_event(EventType.DASHBOARD_DELETED, {}, dashboard['id'])
        return result

    # App methods
    @logging_before_and_after(logger.debug)
    async def get_app(self, uuid: Optional[str] = None, name: Optional[str] = None,
                      create_if_not_exists: bool = True) -> Optional[App]:
        app = await self._base_resource.get_child(App, uuid, name)

        if app:
            logger.info(f'Retrieved menu path {app["name"]} with id {app["id"]}')
        elif create_if_not_exists:
            if not name:
                log_error(logger, f'Name is required to create a menu path', MenuPathError)
            how_many_apps = len(await self.get_apps())
            app = await self._base_resource.create_child(App, alias=name, order=how_many_apps + 1)

            logger.info(f'Created menu path {app["name"]} with id {app["id"]}')
            await self.create_event(EventType.APP_CREATED, {}, app['id'])

        return app

    @logging_before_and_after(logger.debug)
    async def get_apps(self) -> List[App]:
        return await self._base_resource.get_children(App)

    @logging_before_and_after(logger.debug)
    async def delete_app(self, uuid: Optional[str] = None, name: Optional[str] = None) -> bool:
        app = await self.get_app(uuid, name, create_if_not_exists=False)
        result = await self._base_resource.delete_child(App, uuid, name)
        await self.create_event(EventType.APP_DELETED, {}, app['id'])
        if self.api_client.playground:
            dashboards = await self.get_dashboards()
            for dashboard in dashboards:
                if app['id'] in await dashboard.list_app_ids():
                    await dashboard.remove_app(app)
        return result

    @logging_before_and_after(logger.debug)
    async def update_app(self, uuid: Optional[str] = None, name: Optional[str] = None, **params):
        if params.get('new_name') is not None:
            params['name'] = params.pop('new_name')
            params['new_alias'] = True
        app = await self.get_app(uuid, name, create_if_not_exists=False)
        if not app:
            logger.warning(f'App {name} not found, cannot update it')
            return
        await self._base_resource.update_child(App, uuid=uuid, alias=name, **params)
        await self.create_event(EventType.APP_UPDATED, params, app['id'])

    # Role methods
    get_role = get_role
    get_roles = get_roles
    create_role = create_role
    delete_role = delete_role
