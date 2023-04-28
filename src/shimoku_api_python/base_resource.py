import logging
import asyncio
import json

from typing import Optional, Dict, Any, List, TypeVar, Type

from abc import ABC, abstractmethod

from .client import ApiClient
from .exceptions import ResourceIdMissing, CacheError
from .execution_logger import logging_before_and_after, log_error

logger = logging.getLogger(__name__)

HasBaseResource = TypeVar('HasBaseResource', bound='Resource')


class ResourceCache:
    def __init__(self, resource_class: Type[HasBaseResource], parent: HasBaseResource):
        self._parent = parent
        self._resource_class = resource_class
        self._resource_plural = resource_class.plural
        self._cache: Dict[str: HasBaseResource] = {}
        self._aliases: Dict[str: str] = {}
        self._listed = False

    async def list(self) -> List[HasBaseResource]:
        if not self._listed:
            self._listed = True
            endpoint: str = f'{self._parent["base_url"]}{self._parent.resource_type}/' \
                            f'{self._parent["id"]}/{self._resource_plural}'

            resources_raw: Dict = await (
                self._parent.api_client.query_element(
                    endpoint=endpoint, method='GET',
                )
            )
            try:
                resources = resources_raw.get('items')
            except AttributeError:
                logger.warning("Resource's json should have an 'items' field")
                return []

            for resource_dict in resources:
                resource = self._resource_class(uuid=resource_dict.get('id'), parent=self._parent)
                self._cache[resource_dict.get('id')] = resource

                if self._resource_class.alias_field in resource_dict:
                    self._aliases[resource_dict[self._resource_class.alias_field]] = resource_dict.get('id')

                for field, value in resource_dict.items():
                    if field in resource:
                        resource[field] = value if field not in resource.params_to_serialize \
                                          else json.loads(value if value else '{}')

        return list(self._cache.values())

    async def add(self, resource: Optional[HasBaseResource] = None, alias: Optional[str] = None,
                  params: Optional[Dict[str, Any]] = None) -> HasBaseResource:

        if alias:
            await self.raise_if_alias_exists(alias)

        if not resource:
            if not alias:
                log_error(logger, f"Alias is required when resource is not provided", CacheError)

            resource: HasBaseResource = self._resource_class(
                parent=self._parent, alias=alias, **(params if params else {})
            )

            await resource

        resource_id = resource['id']
        if resource.resource_type != self._resource_class.resource_type:
            log_error(logger, f"Resource {resource_id} has the wrong resource type", CacheError)

        if resource_id in self._cache:
            log_error(logger, f"Resource {resource_id} already exists in cache", CacheError)

        if alias:
            self._aliases[alias] = resource_id

        self._cache[resource_id] = resource

        return resource

    async def get(self, uuid: Optional[str] = None, alias: Optional[str] = None) -> Optional[HasBaseResource]:

        if alias in self._aliases:
            uuid = self._aliases[alias]

        if uuid in self._cache:
            return self._cache[uuid]

        if not uuid:
            if alias:
                logger.debug(f"CACHE MISS: Alias {alias}")

                await self.list()

                if alias in self._aliases:
                    uuid = self._aliases[alias]
                    return self._cache[uuid]
                else:
                    logger.debug(f"Alias {alias} not found in business")
                    return None

            log_error(logger, "Resource id or alias have not been provided", CacheError)

        logger.debug(f"CACHE MISS: Resource {uuid}")

        resource = await self._resource_class(parent=self._parent, uuid=uuid)

        return await self.add(resource=resource, alias=alias)

    async def delete(self, uuid: Optional[str] = None, alias: Optional[str] = None):
        resource: HasBaseResource = await self.get(uuid=uuid, alias=alias)
        if not resource:
            log_error(logger, f"Resource {uuid} not found in cache, unable to delete it", CacheError)
        uuid = resource['id']
        await resource.delete()
        del self._cache[uuid]
        self._aliases = {k: v for k, v in self._aliases.items() if v != uuid}

    def cascade_to_dict(self) -> List[Dict[str, Any]]:
        return [resource.cascade_to_dict() for resource in self._cache.values()]

    async def raise_if_alias_exists(self, alias: str):
        await self.list()
        if alias in self._aliases:
            log_error(logger, f"Alias {alias} already exists in cache", CacheError)

    def clear(self):
        self._cache = {}
        self._aliases = {}
        self._listed = False

    def __iter__(self):
        return iter(self._cache.items())

    def __getitem__(self, key):
        return self.get(uuid=key)

    def __len__(self):
        return len(self._cache)

    def __contains__(self, item):
        return item in self._cache

    def __delitem__(self, key):
        return self.delete(uuid=key)


class BaseResource:

    def __init__(
            self, parent: Optional[HasBaseResource] = None, uuid: Optional[str] = None,
            api_client: Optional[ApiClient] = None, params: Optional[Dict[str, Any]] = None,
            alias_field: Optional[str] = None, resource_type: Optional[str] = None,
            params_to_serialize: Optional[List[str]] = None, await_children: Optional[bool] = False
    ):
        self.alias_field = alias_field
        self.resource_type = resource_type

        self.id = uuid
        self.parent = parent
        self.api_client = api_client
        self.children: Dict[Type[HasBaseResource]: ResourceCache] = {}
        self.base_url = ''
        self.params = params if params else {}
        self.params_to_serialize = params_to_serialize if params_to_serialize else []
        self.await_children = await_children

        if parent:
            if not self.parent['id']:
                log_error(logger, f"Parent resource {self.parent.resource_type} has no id",
                          ResourceIdMissing)

            self.base_url = f'{self.parent["base_url"]}{self.parent.resource_type}/{self.parent["id"]}/'

            self.api_client = self.parent.api_client

        if not self.api_client:
            log_error(logger, f"Api client has not been defined", ValueError)

    @logging_before_and_after(logging_level=logger.debug)
    async def async_init(self, wrapper_class_instance: HasBaseResource):
        """
        Initializes the resource asynchronously. If the resource has no id, it will be created, otherwise it will
        fetch the resource and its children from the API.
        """
        if not self.id:
            self.id = await self.create()
        else:
            await self.get()
            await asyncio.gather(*[cache.list() for cache in self.children.values()])

        if self.await_children:
            await asyncio.gather(*[child[1] for c_l in self.children.values() for child in c_l])

        return wrapper_class_instance

    @logging_before_and_after(logging_level=logger.debug)
    async def get(self):
        endpoint = f'{self.base_url}{self.resource_type}/{self.id}'
        resource_dict = await(
            self.api_client.query_element(
                method='GET', endpoint=endpoint,
            )
        )

        for field, value in resource_dict.items():
            if field in self.params:
                self.params[field] = value if field not in self.params_to_serialize\
                    else json.loads(value if value else '{}')

    @logging_before_and_after(logging_level=logger.debug)
    async def create(self) -> str:
        endpoint = f'{self.base_url}{self.resource_type}'

        params = self.params.copy()

        for field in self.params_to_serialize:
            if field in self.params:
                params[field] = json.dumps(params[field])

            assert isinstance(self.params[field], dict)

        return (await(
            self.api_client.query_element(
                method='POST', endpoint=endpoint,
                **{'body_params': params}
            )
        ))['id']

    @logging_before_and_after(logging_level=logger.debug)
    async def update(self):
        endpoint = f'{self.base_url}{self.resource_type}/{self.id}'

        params = self.params.copy()

        for field in self.params_to_serialize:
            if field in self.params:
                params[field] = json.dumps(params[field])

            assert isinstance(self.params[field], dict)

        await(
            self.api_client.query_element(
                method='PATCH', endpoint=endpoint,
                **{'body_params': params}
            )
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def delete(self):
        endpoint = f'{self.base_url}{self.resource_type}/{self.id}'
        await(
            self.api_client.query_element(
                method='DELETE', endpoint=endpoint,
            )
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def create_child(self, resource_class: Type[HasBaseResource], **kwargs) -> HasBaseResource:
        res_cache: ResourceCache = self.children[resource_class]

        if 'uuid' in kwargs:
            log_error(logger, f"Cannot create child with uuid {kwargs['uuid']}, use get instead", ValueError)

        if 'alias' in kwargs:
            await res_cache.raise_if_alias_exists(kwargs['alias'])
            alias = kwargs['alias']
            del kwargs['alias']
            kwargs = dict(alias=alias, params=kwargs)
        else:
            kwargs = dict(params=kwargs)

        return await res_cache.add(**kwargs)

    @logging_before_and_after(logging_level=logger.debug)
    async def get_children(self, resource_class: Type[HasBaseResource]) -> List[HasBaseResource]:
        return await self.children[resource_class].list()

    @logging_before_and_after(logging_level=logger.debug)
    async def get_child(
            self, resource_class: Type[HasBaseResource],
            uuid: Optional[str] = None, alias: Optional[str] = None
    ) -> Any:

        res_cache: ResourceCache = self.children[resource_class]

        child = await res_cache.get(uuid, alias)

        if not child:
            if uuid:
                log_error(logger, f"Resource with id {uuid} not found", ValueError)
            elif alias:
                await res_cache.add(alias=alias)
                child = await res_cache.get(alias=alias)
            else:
                log_error(logger, f"Resource id or alias have not been provided", ValueError)

        return child

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_child(self, resource_class: Type[HasBaseResource],
                           uuid: Optional[str] = None, alias: Optional[str] = None):
        await self.children[resource_class].delete(uuid, alias)

    @logging_before_and_after(logging_level=logger.debug)
    def cascade_to_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the resource.
        """
        resource_dict = {
            'id': self.id,
        }
        resource_dict.update(self.params)

        for resource_class, children in self.children.items():
            resource_dict[resource_class.plural] = children.cascade_to_dict()

        return resource_dict


class Resource(ABC):

    alias_field: Optional[str] = None
    resource_type: Optional[str] = None
    plural: Optional[str] = None

    def __init__(
        self, parent: Optional[HasBaseResource] = None,
        uuid: Optional[str] = None,
        api_client: Optional[ApiClient] = None,
        params: Optional[dict[str, Any]] = None,
        children: Optional[List[Type[HasBaseResource]]] = None,
        check_params_before_creation: Optional[List[str]] = None,
        params_to_serialize: Optional[List[str]] = None,
        await_children: Optional[bool] = False
    ):
        self._base_resource = BaseResource(api_client=api_client, uuid=uuid, parent=parent, params=params,
                                           resource_type=self.resource_type, alias_field=self.alias_field,
                                           params_to_serialize=params_to_serialize, await_children=await_children)

        self._base_resource.children = {
            res_class: ResourceCache(res_class, self) for res_class in children
        } if children else {}

        self._check_params_before_creation = check_params_before_creation if check_params_before_creation else []
        self.api_client = self._base_resource.api_client
        self.params_to_serialize = self._base_resource.params_to_serialize

    def __await__(self):
        """
        Allows the resource to be awaited.
        """
        if not self._base_resource.id:
            for param_name in self._check_params_before_creation:
                if not self._base_resource.params[param_name]:
                    log_error(logger, f"Mandatory parameter {param_name} has not been defined", ValueError)

        return self._base_resource.async_init(self).__await__()

    async def get(self) -> Dict[str, Any]:
        return await self._base_resource.get()

    def cascade_to_dict(self) -> Dict[str, Any]:
        return self._base_resource.cascade_to_dict()

    def __getitem__(self, item):
        if item == 'id':
            return self._base_resource.id
        elif item == 'base_url':
            return self._base_resource.base_url
        elif item in self._base_resource.params:
            return self._base_resource.params[item]
        else:
            log_error(logger, f"{self.__class__.__name__} parameters do not contain {item}", KeyError)

    def __setitem__(self, key, value):
        if key not in self._base_resource.params:
            log_error(logger, f"{self.__class__.__name__} parameters do not contain {key}", KeyError)
        self._base_resource.params[key] = value

    def __contains__(self, item):
        return item in self._base_resource.params

    def __iter__(self):
        return iter(self._base_resource.params)
