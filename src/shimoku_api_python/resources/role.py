from typing import List, Optional, Union, Dict, TypedDict, TYPE_CHECKING
from ..base_resource import Resource
from ..async_execution_pool import async_auto_call_manager

if TYPE_CHECKING:
    from .business import Business
    from .dashboard import Dashboard
    from .app import App

import logging
from ..execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


class Role(Resource):

    resource_type = 'role'
    alias_field = 'role'
    plural = 'roles'

    class RoleParams(TypedDict):
        permission: str
        resource: str
        target: str
        role: str

    @logging_before_and_after(logger.debug)
    def __init__(self, parent: Union['Business', 'Dashboard', 'App'], uuid: Optional[str] = None,
                 alias: Optional[str] = None, db_resource: Optional[Dict] = None):
        params: Role.RoleParams = dict(
            permission='READ',
            resource='BUSINESS_INFO',
            target='GROUP',
            role=alias if alias else '',
        )
        super().__init__(parent=parent, uuid=uuid, check_params_before_creation=['role'], params=params,
                         db_resource=db_resource)

    @logging_before_and_after(logger.debug)
    async def delete(self):
        return await self._base_resource.delete()

    @logging_before_and_after(logger.debug)
    async def update(self):
        return await self._base_resource.update()

    @logging_before_and_after(logger.debug)
    def set_params(self, permission: Optional[str] = None, resource: Optional[str] = None,
                   target: Optional[str] = None, role: Optional[str] = None):

        if permission:
            valid_permissions = ['READ', 'WRITE']
            if permission and permission not in valid_permissions:
                log_error(logger, f'{permission} is not a valid value for permission, '
                                  f'the valid values are: {valid_permissions}', ValueError)
            self._base_resource.params['permission'] = permission
        if resource:
            valid_resources = ['DATA', 'DATA_EXECUTION', 'USER_MANAGEMENT', 'BUSINESS_INFO']
            if resource not in valid_resources:
                log_error(logger, f'{resource} is not a valid value for resource, '
                                  f'the valid values are: {valid_resources}', ValueError)
            self._base_resource.params['resource'] = resource
        if target:
            valid_targets = ['GROUP', 'USER']
            if target and target not in valid_targets:
                log_error(logger, f'{target} is not a valid value for target, '
                                  f'the valid values are: {valid_targets}', ValueError)
            self._base_resource.params['target'] = target
        if role:
            self._base_resource.params['role'] = role


# Parent class methods
@logging_before_and_after(logging_level=logger.debug)
async def create_role(
    self: Union['Business', 'Dashboard', 'App'], role: str, permission: str = 'READ',
    resource: str = 'BUSINESS_INFO', target: str = 'GROUP'
) -> Role:
    return await self._base_resource.create_child(Role, alias=role, permission=permission,
                                                  resource=resource, target=target)


@logging_before_and_after(logging_level=logger.debug)
async def get_role(
    self: Union['Business', 'Dashboard', 'App'], uuid: Optional[str] = None, role: Optional[str] = None
) -> Optional[Role]:
    return await self._base_resource.get_child(Role, uuid, role)


@logging_before_and_after(logging_level=logger.debug)
async def get_roles(
    self: Union['Business', 'Dashboard', 'App']
) -> List[Role]:
    return await self._base_resource.get_children(Role)


@logging_before_and_after(logging_level=logger.debug)
async def delete_role(
    self: Union['Business', 'Dashboard', 'App'], uuid: Optional[str] = None, role: Optional[str] = None
) -> Role:
    return await self._base_resource.delete_child(Role, uuid, role)


# User level methods
@async_auto_call_manager(execute=True)
@logging_before_and_after(logging_level=logger.info)
async def user_create_role(
    self: Union['Business', 'Dashboard', 'App'],
    name: Optional[str] = None, uuid: Optional[str] = None,
    resource: Optional[str] = None, role_name: Optional[str] = None,
    permission: Optional[str] = None, target: Optional[str] = None
) -> Dict:
    """ Create a role
    :param name: name of the parent resource
    :param uuid: UUID of the parent resource
    :param resource: resources level of permission of the role.
    :param role_name: role name
    :param permission: permission level of the role
    :param target: target of the role
    """
    resource_obj = await self._get_for_roles(uuid, name)

    return (await resource_obj.create_role(
                role=role_name, permission=permission, resource=resource, target=target)
            ).cascade_to_dict()


@async_auto_call_manager()
@logging_before_and_after(logging_level=logger.info)
async def user_delete_role(
    self: Union['Business', 'Dashboard', 'App'],
    name: Optional[str] = None, uuid: Optional[str] = None,
    role_id: Optional[str] = None, role_name: Optional[str] = None
):
    """ Delete a role
    :param name: name of the parent resource
    :param uuid: UUID of the parent resource
    :param role_id: UUID of the role to delete
    :param role_name: name of the role to delete
    """
    resource = await self._get_for_roles(uuid, name)

    if resource:
        await resource.delete_role(uuid=role_id, role=role_name)


@async_auto_call_manager(execute=True)
@logging_before_and_after(logging_level=logger.info)
async def user_get_role(
    self: Union['Business', 'Dashboard', 'App'],
    name: Optional[str] = None, uuid: Optional[str] = None,
    role_name: Optional[str] = None
) -> List[Dict]:
    """ Get the list of roles by name
    :param name: name of the parent resource
    :param uuid: UUID of the parent resource
    :param role_name: name of the role
    :return: list of roles of the dashboard
    """
    resource = await self._get_for_roles(uuid, name)

    if resource:
        role = await resource.get_role(role=role_name)
        if role:
            return role.cascade_to_dict()
        logger.info(f'Role {role_name} not found in {str(resource)}')

    return []


@async_auto_call_manager(execute=True)
@logging_before_and_after(logging_level=logger.info)
async def user_get_roles(
    self: Union['Business', 'Dashboard', 'App'],
    name: Optional[str] = None, uuid: Optional[str] = None
) -> List[Dict]:
    """ Get the list of roles
    :param name: name of the parent resource
    :param uuid: UUID of the parent resource
    :return: list of roles of the dashboard
    """
    resource = await self._get_for_roles(uuid, name)

    if resource:
        return [role.cascade_to_dict() for role in await resource.get_roles()]

    return []
