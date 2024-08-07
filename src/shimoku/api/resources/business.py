from uuid import uuid1
from typing import Optional, TYPE_CHECKING

from shimoku.api.base_resource import Resource
from shimoku.api.resources.business_user import BusinessUser, BusinessInvitation
from shimoku.api.resources.role import (
    Role,
    create_role,
    get_role,
    get_roles,
    delete_role,
)
from shimoku.api.resources.event import Event
from shimoku.api.resources.dashboard import Dashboard
from shimoku.api.resources.app import App

from shimoku.utils import EventType
from shimoku.exceptions import WorkspaceError, MenuPathError, BoardError, RoleError

if TYPE_CHECKING:
    from shimoku.api.resources.universe import Universe

import logging
from shimoku.execution_logger import log_error

logger = logging.getLogger(__name__)


class Business(Resource):
    _module_logger = logger
    resource_type = "business"
    alias_field = "name"
    plural = "businesses"

    def __init__(
        self,
        parent: "Universe",
        uuid: Optional[str] = None,
        alias: Optional[str] = None,
        db_resource: Optional[dict] = None,
    ):
        params = {
            "name": alias if alias else "",
            "theme": {},
        }

        super().__init__(
            parent=parent,
            uuid=uuid,
            db_resource=db_resource,
            children=[Dashboard, App, Role, Event, BusinessUser, BusinessInvitation],
            check_params_before_creation=["name"],
            params_to_serialize=["theme"],
            params=params,
        )

        self.currently_in_use = False

    async def delete(self):
        if self.currently_in_use:
            log_error(
                logger,
                f"Workspace {str(self)} is currently in use and cannot be deleted",
                WorkspaceError,
            )
        return await self._base_resource.delete()

    async def update(self):
        return await self._base_resource.update()

    # Event methods
    async def create_event(
        self, event_type: EventType, content: dict, resource_id: Optional[str] = None
    ):
        """Creates an event but do not store it in the cache
        :param event_type: The type of the event
        :param content: The content of the event
        :param resource_id: The id of the resource that triggered the event
        """
        event = Event(parent=self)
        event.set_params(type=event_type.value, content=content, resourceId=resource_id)
        logger.info(f"Event {event_type.value} created")
        await event

    # Dashboard methods
    async def create_dashboard(
        self,
        name: str,
        order: int,
        is_public: bool = False,
        is_disabled: bool = False,
        theme: Optional[dict] = None,
    ) -> Dashboard:
        dashboard_metadata = dict(
            order=order,
            isDisabled=is_disabled,
            theme=theme or self["theme"],
        )
        if is_public:
            dashboard_metadata["publicPermission"] = dict(
                isPublic=True, permission="READ", token=str(uuid1())
            )
        dashboard = await self._base_resource.create_child(
            Dashboard, alias=name, **dashboard_metadata
        )
        logger.info(f'Board {name} created with id {dashboard["id"]}')
        return dashboard

    async def update_dashboard(
        self, uuid: Optional[str] = None, name: Optional[str] = None, **params
    ):
        if params.get("new_name") is not None:
            params["name"] = params.pop("new_name")
            params["new_alias"] = True
        dashboard = await self.get_dashboard(uuid, name, create_if_not_exists=False)
        if not dashboard:
            logger.warning(f"Board {name} not found, cannot update it")
            return
        await self._base_resource.update_child(
            Dashboard, uuid=dashboard["id"], **params
        )

    async def get_dashboard(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        create_if_not_exists: bool = True,
    ) -> Optional[Dashboard]:
        dashboard = await self._base_resource.get_child(Dashboard, uuid, name)

        if dashboard:
            logger.info(
                f'Retrieved board {dashboard["name"]} with id {dashboard["id"]}'
            )
        elif create_if_not_exists:
            if not name:
                log_error(logger, "Name is required to create a board", BoardError)
            how_many_dashboards = len(await self.get_dashboards())
            dashboard = await self._base_resource.create_child(
                Dashboard, alias=name, order=how_many_dashboards + 1
            )
            logger.info(f'Created board {dashboard["name"]} with id {dashboard["id"]}')

        return dashboard

    async def get_dashboards(self) -> list[Dashboard]:
        return await self._base_resource.get_children(Dashboard)

    async def delete_dashboard(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> bool:
        dashboard = await self.get_dashboard(uuid, name, create_if_not_exists=False)
        result = await self._base_resource.delete_child(Dashboard, uuid, name)
        return result

    # App methods
    async def get_app(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        create_if_not_exists: bool = True,
    ) -> Optional[App]:
        app = await self._base_resource.get_child(App, uuid, name)

        if app:
            logger.info(f'Retrieved menu path {app["name"]} with id {app["id"]}')
        elif create_if_not_exists:
            if not name:
                log_error(
                    logger, "Name is required to create a menu path", MenuPathError
                )
            how_many_apps = len(await self.get_apps())
            app = await self._base_resource.create_child(
                App, alias=name, order=how_many_apps + 1
            )

            logger.info(f'Created menu path {app["name"]} with id {app["id"]}')

        return app

    async def get_apps(self) -> list[App]:
        return await self._base_resource.get_children(App)

    async def delete_app(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> bool:
        app = await self.get_app(uuid, name, create_if_not_exists=False)
        result = await self._base_resource.delete_child(App, uuid, name)
        if self.api_client.playground:
            dashboards = await self.get_dashboards()
            for dashboard in dashboards:
                if app["id"] in await dashboard.list_app_ids():
                    await dashboard.remove_app(app)
        return result

    async def update_app(
        self, uuid: Optional[str] = None, name: Optional[str] = None, **params
    ):
        if params.get("new_name") is not None:
            params["name"] = params.pop("new_name")
            params["new_alias"] = True
        app = await self.get_app(uuid, name, create_if_not_exists=False)
        if not app:
            logger.warning(f"App {name} not found, cannot update it")
            return
        await self._base_resource.update_child(App, uuid=uuid, alias=name, **params)

    # Account methods
    async def invite_user(
        self, email: str, roles: list[str], send_email: bool
    ) -> BusinessInvitation:
        invitation = await self._base_resource.create_child(
            BusinessInvitation, email=email, roles=roles, sendEmail=send_email
        )
        logger.info(f"Invitation sent to ({email})")
        return invitation

    async def get_pending_invitations(self):
        return await self._base_resource.get_children(BusinessInvitation)

    async def delete_pending_invitation(self, email: str):
        return await self._base_resource.delete_child(BusinessInvitation, alias=email)

    async def get_users(self):
        return await self._base_resource.get_children(BusinessUser)

    async def delete_user(self, email: str):
        return await self._base_resource.delete_child(BusinessUser, alias=email)

    # Role methods
    get_role = get_role
    get_roles = get_roles
    create_role = create_role
    delete_role = delete_role
