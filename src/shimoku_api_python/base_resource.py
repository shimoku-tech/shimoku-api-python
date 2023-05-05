import logging
import asyncio
import json

from typing import Optional, Dict, Any, List, TypeVar, Type, Set
from tqdm import tqdm

from abc import ABC, abstractmethod

from .client import ApiClient
from .exceptions import ResourceIdMissing, CacheError
from .execution_logger import logging_before_and_after, log_error

logger = logging.getLogger(__name__)

IsResource = TypeVar('IsResource', bound='Resource')


class ResourceCache:

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, resource_class: Type[IsResource], parent: IsResource):
        self._parent = parent
        self._resource_class = resource_class
        self._resource_plural = resource_class.plural
        self._cache: Dict[str: IsResource] = {}
        self._aliases: Dict[str: str] = {}
        self._listed = False
        self.listing_lock = None

    @logging_before_and_after(logging_level=logger.debug)
    async def list(self) -> List[IsResource]:

        if not self.listing_lock:
            self.listing_lock = asyncio.Lock()

        async with self.listing_lock:

            if self._listed:
                return list(self._cache.values())

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
                                          else json.loads(value if value else f'{resource[field].__class__()}')
                resource.empty_changed_params()

        return list(self._cache.values())

    @logging_before_and_after(logging_level=logger.debug)
    async def add(self, resource: Optional[IsResource] = None, alias: Optional[str] = None,
                  params: Optional[Dict[str, Any]] = None) -> IsResource:

        if alias:
            await self.raise_if_alias_exists(alias)

        if not resource:
            if not alias:
                log_error(logger, f"Alias is required when resource is not provided", CacheError)

            resource: IsResource = self._resource_class(parent=self._parent, alias=alias)

        if not resource['id']:
            resource.set_params(**params) if params else None
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

    @logging_before_and_after(logging_level=logger.debug)
    async def get(self, uuid: Optional[str] = None, alias: Optional[str] = None) -> Optional[IsResource]:

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
                    logger.debug(f"Alias {alias} not found in cache")
                    return None

            log_error(logger, "Resource id or alias have not been provided", CacheError)

        logger.debug(f"CACHE MISS: Resource {uuid}")

        resource = await self._resource_class(parent=self._parent, uuid=uuid)

        return await self.add(resource=resource, alias=alias)

    @logging_before_and_after(logging_level=logger.debug)
    async def update(self, uuid: Optional[str] = None, alias: Optional[str] = None, **params
                     ) -> bool:

        resource: IsResource = await self.get(uuid=uuid, alias=alias)
        if not resource:
            return False

        if params.get('new_alias'):
            await self.raise_if_alias_exists(params['new_alias'])
            params[resource.alias_field] = params['new_alias']
            del params['new_alias']
            del self._aliases[resource[resource.alias_field]]
            self._aliases[params[resource.alias_field]] = resource['id']

        resource.set_params(**params)
        await resource.update()

        return True

    @logging_before_and_after(logging_level=logger.debug)
    async def delete(self, uuid: Optional[str] = None, alias: Optional[str] = None) -> bool:
        resource: IsResource = await self.get(uuid=uuid, alias=alias)
        if not resource:
            log_error(logger, f"Resource {uuid} not found in cache, unable to delete it", CacheError)
            return False
        uuid = resource['id']
        await resource.delete()
        del self._cache[uuid]
        self._aliases = {k: v for k, v in self._aliases.items() if v != uuid}
        return True

    @logging_before_and_after(logging_level=logger.debug)
    async def raise_if_alias_exists(self, alias: str):
        await self.list()
        if alias in self._aliases:
            log_error(logger, f"Alias {alias} already exists in cache", CacheError)

    # @logging_before_and_after(logging_level=logger.debug)
    def cascade_to_dict(self) -> List[Dict[str, Any]]:
        return [resource.cascade_to_dict() for resource in self._cache.values()]

    # @logging_before_and_after(logging_level=logger.debug)
    def cascade_update_locks(self):
        """ Update the local lock and the locks of all the resources in the cache"""
        self.listing_lock = asyncio.Lock()
        for resource in self._cache.values():
            resource.cascade_update_locks()

    @logging_before_and_after(logging_level=logger.debug)
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
    """ Base class for all the resources in the API """
    def __init__(
            self, parent: Optional[IsResource] = None, uuid: Optional[str] = None,
            api_client: Optional[ApiClient] = None, params: Optional[Dict[str, Any]] = None,
            alias_field: Optional[str] = None, resource_type: Optional[str] = None,
            params_to_serialize: Optional[List[str]] = None, await_children: Optional[bool] = False,
            wrapper_class_instance: Optional[IsResource] = None
    ):
        self.alias_field = alias_field
        self.resource_type = resource_type

        self.id = uuid
        self.parent = parent
        self.api_client = api_client
        self.children: Dict[Type[IsResource]: ResourceCache] = {}
        self.base_url = ''
        self.params = params if params else {}
        self.changed_params: Set[str] = set()
        self.params_to_serialize = params_to_serialize if params_to_serialize else []
        self.await_children = await_children
        self.wrapper_class_instance = wrapper_class_instance

        if parent:
            if not self.parent['id']:
                log_error(logger, f"Parent resource {self.parent.resource_type} has no id",
                          ResourceIdMissing)

            self.base_url = f'{self.parent["base_url"]}{self.parent.resource_type}/{self.parent["id"]}/'

            self.api_client = self.parent.api_client

        if not self.api_client:
            log_error(logger, f"Api client has not been defined", ValueError)

    @logging_before_and_after(logging_level=logger.debug)
    async def async_init(self):
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

        return self.wrapper_class_instance

    @logging_before_and_after(logging_level=logger.debug)
    async def get(self):
        """ Fetches the resource from the API and updates the params. """
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

        self.changed_params = set()

    @logging_before_and_after(logging_level=logger.debug)
    async def create(self) -> str:
        """ Creates the resource in the API with the current params. """
        endpoint = f'{self.base_url}{self.resource_type}'

        self.changed_params = set()

        params = self.params.copy()

        for field in self.params_to_serialize:
            if field in self.params:
                params[field] = json.dumps(params[field])

            assert isinstance(self.params[field], (dict, list))

        return (await(
            self.api_client.query_element(
                method='POST', endpoint=endpoint,
                **{'body_params': params}
            )
        ))['id']

    @logging_before_and_after(logging_level=logger.debug)
    async def update(self):
        """ Updates the resource in the API with the current params. """
        endpoint = f'{self.base_url}{self.resource_type}/{self.id}'

        params = {k: v for k, v in self.params.items() if k in self.changed_params}

        for field in self.params_to_serialize:
            if field in params:
                params[field] = json.dumps(params[field])

            assert isinstance(self.params[field], dict)

        await(
            self.api_client.query_element(
                method='PATCH', endpoint=endpoint,
                **{'body_params': params}
            )
        )

        self.changed_params = set()

    @logging_before_and_after(logging_level=logger.debug)
    async def delete(self):
        """ Deletes the resource from the API. """
        endpoint = f'{self.base_url}{self.resource_type}/{self.id}'
        await(
            self.api_client.query_element(
                method='DELETE', endpoint=endpoint,
            )
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def create_children_batch(self, resource_class: Type[IsResource], children_params: List[Dict],
                                    batch_size: int = 100):
        """ Creates a batch of children of a given resource class. It doesn't return the created resources,
        And it doesn't save them in the cache.
        :param resource_class: The class of the resource to create.
        :param children_params: The parameters of the resources to create.
        :param batch_size: The size of the batch to create.
        """
        if batch_size >= 1000:
            raise ValueError('batch_size must be less than 1000')

        endpoint = f'{self.base_url}{self.resource_type}/{self.id}/{resource_class.resource_type}/batch'

        log_level = logger.getEffectiveLevel()
        if log_level >= logging.INFO:
            logger.info("Uploading table data")

        with tqdm(total=len(children_params), unit=' report entries', disable=(log_level > logging.INFO)) \
                as progress_bar:
            query_tasks = []
            for chunk in range(0, len(children_params), batch_size):
                query_tasks.append(
                    self.api_client.query_element(
                        method='POST', endpoint=endpoint,
                        **{'body_params': children_params[chunk:chunk + batch_size],
                           'progress_bar': (progress_bar, len(children_params[chunk:chunk + batch_size]))},
                    )
                )
            await asyncio.gather(*query_tasks)

        logger.info("Table data uploaded")

    @logging_before_and_after(logging_level=logger.debug)
    async def create_child(self, resource_class: Type[IsResource], **kwargs) -> IsResource:
        """ Creates a child of a given resource class.
        :param resource_class: The class of the resource to create.
        :param kwargs: The parameters of the resource to create.
        :return: The created resource.
        """
        res_cache: ResourceCache = self.children[resource_class]

        if 'uuid' in kwargs:
            log_error(logger, f"Cannot create child with uuid {kwargs['uuid']}, use get instead", ValueError)

        if 'alias' in kwargs:
            if kwargs['alias'] is None:
                log_error(logger, f"Cannot create child with alias None", ValueError)
            await res_cache.raise_if_alias_exists(kwargs['alias'])
            alias = kwargs['alias']
            del kwargs['alias']
            kwargs = dict(alias=alias, params=kwargs)
        else:
            resource = resource_class(parent=self.wrapper_class_instance)
            kwargs = dict(resource=resource, params=kwargs)

        return await res_cache.add(**kwargs)

    @logging_before_and_after(logging_level=logger.debug)
    async def update_child(self, resource_class: Type[IsResource],
                           uuid: Optional[str] = None, alias: Optional[str] = None,
                           **params) -> bool:
        """ Updates a child of a given resource class.
        :param resource_class: The class of the resource to update.
        :param uuid: The uuid of the resource to update.
        :param alias: The alias of the resource to update.
        :param params: The parameters of the resource to update.
        :return: True if the resource was updated, False otherwise.
        """
        return await self.children[resource_class].update(uuid=uuid, alias=alias, **params)

    @logging_before_and_after(logging_level=logger.debug)
    async def get_children(self, resource_class: Type[IsResource]) -> List[IsResource]:
        """ Gets all children of a given resource class.
        :param resource_class: The class of the resources to get.
        :return: A list of resources.
        """
        return await self.children[resource_class].list()

    @logging_before_and_after(logging_level=logger.debug)
    async def get_child(
            self, resource_class: Type[IsResource],
            uuid: Optional[str] = None, alias: Optional[str] = None,
            create_if_not_exists: bool = False
    ) -> Optional[IsResource]:
        """ Gets a child resource.
        :param resource_class: The class of the resource to get.
        :param uuid: The uuid of the resource to get.
        :param alias: The alias of the resource to get.
        :param create_if_not_exists: If True, creates the resource if it does not exist.
        """
        if not uuid and not alias:
            log_error(logger, f"Cannot get child without uuid or alias", ValueError)

        res_cache: ResourceCache = self.children[resource_class]

        child = await res_cache.get(uuid, alias)

        if not child and alias and create_if_not_exists:
            child = await self.create_child(resource_class, alias=alias)

        return child

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_child(self, resource_class: Type[IsResource],
                           uuid: Optional[str] = None, alias: Optional[str] = None) -> bool:
        """ Deletes a child resource.
        :param resource_class: The class of the resource to delete.
        :param uuid: The uuid of the resource to delete.
        :param alias: The alias of the resource to delete.
        """
        return await self.children[resource_class].delete(uuid, alias)

    # @logging_before_and_after(logging_level=logger.debug)
    def cascade_to_dict(self) -> Dict[str, Any]:
        """ Returns a dictionary representation of the resource and its children.
        :return: A dictionary representation of the resource and its children.
        """
        resource_dict = {
            'id': self.id,
        }
        resource_dict.update(self.params)

        for resource_class, children in self.children.items():
            resource_dict[resource_class.plural] = children.cascade_to_dict()

        return resource_dict

    # @logging_before_and_after(logging_level=logger.debug)
    def cascade_update_locks(self):
        """ Updates the locks of all children. """
        for resource_class, children in self.children.items():
            children.cascade_update_locks()

    def __str__(self):
        """ Returns a string representation of the resource. """
        return self.params[self.alias_field] if self.alias_field else self.id


class Resource(ABC):

    alias_field: Optional[str] = None
    resource_type: Optional[str] = None
    plural: Optional[str] = None

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(
        self, parent: Optional[IsResource] = None,
        uuid: Optional[str] = None,
        api_client: Optional[ApiClient] = None,
        params: Optional[dict[str, Any]] = None,
        children: Optional[List[Type[IsResource]]] = None,
        check_params_before_creation: Optional[List[str]] = None,
        params_to_serialize: Optional[List[str]] = None,
        await_children: Optional[bool] = False
    ):
        self._base_resource = BaseResource(api_client=api_client, uuid=uuid, parent=parent, params=params,
                                           resource_type=self.resource_type, alias_field=self.alias_field,
                                           params_to_serialize=params_to_serialize, await_children=await_children,
                                           wrapper_class_instance=self)

        self._base_resource.children = {
            res_class: ResourceCache(res_class, self) for res_class in children
        } if children else {}

        self._check_params_before_creation = check_params_before_creation if check_params_before_creation else []
        self.api_client = self._base_resource.api_client
        self.params_to_serialize = self._base_resource.params_to_serialize

    @logging_before_and_after(logging_level=logger.debug)
    def __await__(self):
        """ Allows the resource to be awaited. """
        if not self._base_resource.id:
            for param_name in self._check_params_before_creation:
                if self._base_resource.params[param_name] is None:
                    log_error(logger, f"Mandatory parameter {param_name} has not been defined", ValueError)

        return self._base_resource.async_init().__await__()

    @logging_before_and_after(logging_level=logger.debug)
    async def get(self) -> Dict[str, Any]:
        return await self._base_resource.get()

    # @logging_before_and_after(logging_level=logger.debug)
    def cascade_to_dict(self) -> Dict[str, Any]:
        """ Returns a dictionary representation of the resource and its children. """
        return self._base_resource.cascade_to_dict()

    # @logging_before_and_after(logging_level=logger.debug)
    def cascade_update_locks(self):
        """ Updates all locks of the children. """
        self._base_resource.cascade_update_locks()

    @logging_before_and_after(logging_level=logger.debug)
    def set_params(self, **kwargs):
        """ Sets the parameters of the resource. """
        for key, value in kwargs.items():
            if isinstance(key, tuple) and len(key) == 2 and isinstance(key[0], str) and isinstance(key[1], str):
                value[key[0]][key[1]] = value
            elif value is not None:
                self[key] = value

    @logging_before_and_after(logging_level=logger.debug)
    def empty_changed_params(self):
        """ Empties the changed_params set. """
        self._base_resource.changed_params = set()

    def __getitem__(self, item):
        """ Returns the value of the parameter with the given name. """
        if item == 'id':
            return self._base_resource.id
        elif item == 'base_url':
            return self._base_resource.base_url
        elif item in self._base_resource.params:
            return self._base_resource.params[item]
        else:
            log_error(logger, f"{self.__class__.__name__} parameters do not contain {item}", KeyError)

    def __setitem__(self, key, value):
        """ Sets the value of the parameter with the given name. """
        if key not in self._base_resource.params:
            log_error(logger, f"{self.__class__.__name__} parameters do not contain {key}", KeyError)
        class_type = self._base_resource.params[key].__class__
        if not isinstance(value, class_type) \
                and not isinstance(self._base_resource.params[key], type(None)) and not isinstance(value, type(None)):
            log_error(logger, f"Value {value} with type {value.__class__} for parameter {key} "
                              f"is not of type {self._base_resource.params[key].__class__}", ValueError)
        self._base_resource.params[key] = value if value else class_type()
        self._base_resource.changed_params.add(key)

    def __contains__(self, item):
        """ Returns whether the resource contains a parameter with the given name. """
        return item in self._base_resource.params

    def __iter__(self):
        """ Returns an iterator over the parameters of the resource. """
        return iter(self._base_resource.params)

    def __str__(self):
        """ Returns a string representation of the resource. """
        return self._base_resource.__str__()
