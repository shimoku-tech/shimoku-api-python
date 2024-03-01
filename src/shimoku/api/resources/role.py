from typing import Union, Optional, TypedDict, TYPE_CHECKING
from shimoku.api.base_resource import Resource

if TYPE_CHECKING:
    from shimoku.api.resources.business import Business
    from shimoku.api.resources.dashboard import Dashboard
    from shimoku.api.resources.app import App
    from shimoku.api.user_access_classes.businesses_layer import WorkspacesLayer
    from shimoku.api.user_access_classes.apps_layer import MenuPathsLayer
    from shimoku.api.user_access_classes.dashboards_layer import BoardsLayer
import logging
from shimoku.execution_logger import log_error

logger = logging.getLogger(__name__)

VALID_PERMISSIONS = ["READ", "WRITE"]
VALID_RESOURCES = ["DATA", "DATA_EXECUTION", "USER_MANAGEMENT", "BUSINESS_INFO"]
VALID_TARGETS = ["GROUP", "USER"]


class Role(Resource):
    resource_type = "role"
    alias_field = "role"
    plural = "roles"

    class RoleParams(TypedDict):
        permission: str
        resource: str
        target: str
        role: str

    def __init__(
        self,
        parent: Union["Business", "Dashboard", "App"],
        uuid: Optional[str] = None,
        alias: Optional[str] = None,
        db_resource: Optional[dict] = None,
    ):
        params: Role.RoleParams = dict(
            permission="READ",
            resource="BUSINESS_INFO",
            target="GROUP",
            role=alias if alias else "",
        )
        super().__init__(
            parent=parent,
            uuid=uuid,
            check_params_before_creation=["role"],
            params=params,
            db_resource=db_resource,
        )

    async def delete(self):
        return await self._base_resource.delete()

    async def update(self):
        return await self._base_resource.update()

    def set_params(
        self,
        permission: Optional[str] = None,
        resource: Optional[str] = None,
        target: Optional[str] = None,
        role: Optional[str] = None,
    ):
        if permission:
            if permission and permission not in VALID_PERMISSIONS:
                log_error(
                    logger,
                    f"{permission} is not a valid value for permission, "
                    f"the valid values are: {VALID_PERMISSIONS}",
                    ValueError,
                )
            self._base_resource.params["permission"] = permission
        if resource:
            if resource not in VALID_RESOURCES:
                log_error(
                    logger,
                    f"{resource} is not a valid value for resource, "
                    f"the valid values are: {VALID_RESOURCES}",
                    ValueError,
                )
            self._base_resource.params["resource"] = resource
        if target:
            if target and target not in VALID_TARGETS:
                log_error(
                    logger,
                    f"{target} is not a valid value for target, "
                    f"the valid values are: {VALID_TARGETS}",
                    ValueError,
                )
            self._base_resource.params["target"] = target
        if role:
            self._base_resource.params["role"] = role


# Parent class methods
async def create_role(
    self: Union["Business", "Dashboard", "App"],
    role: str,
    permission: str = "READ",
    resource: str = "BUSINESS_INFO",
    target: str = "GROUP",
) -> Role:
    return await self._base_resource.create_child(
        Role, alias=role, permission=permission, resource=resource, target=target
    )


async def get_role(
    self: Union["Business", "Dashboard", "App"],
    uuid: Optional[str] = None,
    role: Optional[str] = None,
) -> Optional[Role]:
    return await self._base_resource.get_child(Role, uuid, role)


async def get_roles(self: Union["Business", "Dashboard", "App"]) -> list[Role]:
    return await self._base_resource.get_children(Role)


async def delete_role(
    self: Union["Business", "Dashboard", "App"],
    uuid: Optional[str] = None,
    role: Optional[str] = None,
) -> Role:
    return await self._base_resource.delete_child(Role, uuid, role)


# User level methods
async def user_create_role(
    self: Union["WorkspacesLayer", "MenuPathsLayer", "BoardsLayer"],
    uuid: Optional[str] = None,
    name: Optional[str] = None,
    resource: Optional[str] = None,
    role_name: Optional[str] = None,
    permission: Optional[str] = None,
    target: Optional[str] = None,
) -> dict:
    """
    Create a new role at the resource level
    :param name: name of the resource
    :param uuid: uuid of the resource
    :param resource: resource of the role
    :param role_name: name of the role
    :param permission: permission of the role
    :param target: target of the role
    """
    resource_obj = await self._get_for_roles(uuid, name)

    return (
        await resource_obj.create_role(
            role=role_name, permission=permission, resource=resource, target=target
        )
    ).cascade_to_dict()


async def user_delete_role(
    self: Union["WorkspacesLayer", "MenuPathsLayer", "BoardsLayer"],
    uuid: Optional[str] = None,
    name: Optional[str] = None,
    role_id: Optional[str] = None,
    role_name: Optional[str] = None,
):
    """
    Delete the role at the resource level
    :param name: name of the resource
    :param uuid: uuid of the resource
    :param role_id: id of the role
    :param role_name: name of the role
    """
    resource = await self._get_for_roles(uuid, name)

    if resource:
        await resource.delete_role(uuid=role_id, role=role_name)


async def user_get_role(
    self: Union["WorkspacesLayer", "MenuPathsLayer", "BoardsLayer"],
    uuid: Optional[str] = None,
    name: Optional[str] = None,
    role_name: Optional[str] = None,
) -> list[dict]:
    """
    Get the role at the resource level
    :param name: name of the resource
    :param uuid: uuid of the resource
    :param role_name: name of the role
    """
    resource = await self._get_for_roles(uuid, name)

    if resource:
        role = await resource.get_role(role=role_name)
        if role:
            return role.cascade_to_dict()
        logger.info(f"Role {role_name} not found in {str(resource)}")

    return []


async def user_get_roles(
    self: Union["WorkspacesLayer", "MenuPathsLayer", "BoardsLayer"],
    uuid: Optional[str] = None,
    name: Optional[str] = None,
) -> list[dict]:
    """
    Get the roles at the resource level
    :param name: name of the resource
    :param uuid: uuid of the resource
    """
    resource = await self._get_for_roles(uuid, name)

    if resource:
        return [role.cascade_to_dict() for role in await resource.get_roles()]

    return []
