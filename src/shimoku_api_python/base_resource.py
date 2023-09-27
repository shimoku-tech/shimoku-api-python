import logging
import asyncio
import json

from typing import Optional, Dict, Any, List, TypeVar, Type, Set, Tuple, Union, NewType
from tqdm import tqdm

from abc import ABC

from .client import ApiClient
from .exceptions import ResourceIdMissing, CacheError
from .execution_logger import logging_before_and_after, log_error

logger = logging.getLogger(__name__)

IsResource = TypeVar('IsResource', bound='Resource')
Alias = NewType('Alias', Union[str, Tuple[str, ...]])
AliasField = NewType('AliasField', Union[str, Tuple[str, ...]])


class ResourceCache:

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(
            self, resource_class: Type[IsResource], parent: IsResource
    ):
        self._parent = parent
        self._resource_class = resource_class
        self._resource_plural = resource_class.plural
        self._cache: Dict[str: IsResource] = {}
        self._aliases: Dict[str: str] = {}
        self._listed = False
        self._listing_lock = None

    @logging_before_and_after(logging_level=logger.debug)
    async def list(
            self, limit: Optional[int] = None
    ) -> List[IsResource]:
        """ List all child resources
        :param limit: Limit the number of resources to be listed
        :return: List of resources
        """
        if not self._listing_lock:
            self._listing_lock = asyncio.Lock()

        async with self._listing_lock:

            if self._parent.api_client.cache_enabled:
                if self._listed:
                    logger.debug("Resource cache already listed")
                    return list(self._cache.values())
            else:
                await asyncio.gather(
                    *[resource.update()
                      for resource in self._cache.values()
                      if 'dirty' in dir(resource) and resource.dirty]
                )
                self._cache = {}
                self._aliases = {}

            self._listed = True
            endpoint: str = f'{self._parent["base_url"]}{self._parent.resource_type}/' \
                            f'{self._parent["id"]}/{self._resource_plural}'

            resources_raw: Dict = await (
                self._parent.api_client.query_element(
                    endpoint=endpoint, method='GET', limit=limit,
                    elastic_supported=self._resource_class.elastic_supported
                )
            )
            try:
                resources = resources_raw.get('items') if isinstance(resources_raw, dict) else resources_raw
                if not isinstance(resources, list):
                    raise AttributeError()
            except AttributeError:
                logger.warning("Resource's json should have an 'items' field")
                return []

            # Sort resources by id to ensure consistent ordering for alias collision resolution
            resources = sorted(resources, key=lambda x: x.get('id'))

            for resource_dict in resources:
                resource = self._resource_class(db_resource=resource_dict, parent=self._parent)
                alias_entry = resource['alias']
                if alias_entry:
                    if alias_entry in self._aliases:
                        continue
                    self._aliases[alias_entry] = resource_dict.get('id')
                self._cache[resource_dict.get('id')] = resource
                resource.empty_changed_params()

        self._listing_lock = None
        return list(self._cache.values())

    @logging_before_and_after(logging_level=logger.debug)
    async def add(
            self, resource: Optional[IsResource] = None, alias: Optional[Alias] = None,
            params: Optional[Dict[str, Any]] = None
    ) -> IsResource:
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
            if self._parent.api_client.cache_enabled:
                log_error(logger, f"Resource {resource_id} already exists in cache", CacheError)
            del self._cache[resource_id]
            for alias_key, alias_value in list(self._aliases.items()):
                if alias_value == resource_id:
                    del self._aliases[alias_key]
                    break

        alias = resource['alias']

        if alias is not None:
            self._aliases[alias] = resource_id

        self._cache[resource_id] = resource

        return resource

    @logging_before_and_after(logging_level=logger.debug)
    async def get(
            self, uuid: Optional[str] = None, alias: Optional[Alias] = None
    ) -> Optional[IsResource]:
        if uuid and alias:
            log_error(logger, "Only one of uuid or alias can be provided", CacheError)

        if self._parent.api_client.cache_enabled:
            if alias in self._aliases:
                uuid = self._aliases[alias]

            if uuid in self._cache:
                logger.debug(f"CACHE HIT: Resource {uuid}")
                return self._cache[uuid]

        if not uuid:
            if alias is not None:
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

        db_resource = await self._resource_class(parent=self._parent, uuid=uuid).get()
        resource = self._resource_class(parent=self._parent, db_resource=db_resource)

        return await self.add(resource=resource, alias=alias)

    @logging_before_and_after(logging_level=logger.debug)
    async def update(
        self, uuid: Optional[str] = None, alias: Optional[Alias] = None, **params
    ) -> bool:
        resource: IsResource = await self.get(uuid=uuid, alias=alias)
        if not resource:
            return False

        if params.get('new_alias'):
            new_alias = resource.get_alias_from_other_params(params)
            await self.raise_if_alias_exists(new_alias)
            del self._aliases[resource['alias']]
            self._aliases[new_alias] = resource['id']
            del params['new_alias']

        resource.set_params(**params)
        await resource.update()

        return True

    @logging_before_and_after(logging_level=logger.debug)
    async def delete(
            self, uuid: Optional[str] = None, alias: Optional[Alias] = None
    ) -> bool:
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
    async def raise_if_alias_exists(self, alias: Alias):
        await self.list()
        if alias in self._aliases:
            if self._parent.api_client.cache_enabled:
                log_error(logger, f"Alias {alias} already exists in cache", CacheError)
            del self._aliases[alias]

    # @logging_before_and_after(logging_level=logger.debug)
    def cascade_to_dict(self) -> List[Dict[str, Any]]:
        return [resource.cascade_to_dict() for resource in self._cache.values()]

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
        alias_field: Optional[AliasField] = None, resource_type: Optional[str] = None,
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

            self.api_client: ApiClient = self.parent.api_client

        if not self.api_client:
            log_error(logger, f"Api client has not been defined", ValueError)

    @logging_before_and_after(logging_level=logger.debug)
    def get_alias_field_value(self, alias_field: str, params: Optional[dict]) -> str:
        """ Returns the value of one of the fields used to create the alias
        :param alias_field: The name of the field
        :param params: The params to use to get the value of the field
        :return: The value of the field
        """
        if not params:
            params = self.params
        path = alias_field.split('/')
        alias = params[path[0]]
        for path_step in path[1:]:
            alias = alias[path_step]
        return alias

    @logging_before_and_after(logging_level=logger.debug)
    def get_alias(self, params: Optional[dict] = None) -> Optional[Alias]:
        if self.alias_field:
            if isinstance(self.alias_field, tuple):
                return tuple(self.get_alias_field_value(alias_field, params=params) for alias_field in self.alias_field)
            if isinstance(self.alias_field, str):
                return self.get_alias_field_value(self.alias_field, params=params)
            log_error(logger, f"Alias field {self.alias_field} is not a string or a tuple", ValueError)
        else:
            return None

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

        if self.await_children:
            await asyncio.gather(*[cache.list() for cache in self.children.values()])
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
                self.params[field] = value if field not in self.params_to_serialize \
                    else json.loads(value if value else '{}')

        self.changed_params = set()
        return resource_dict

    @logging_before_and_after(logging_level=logger.debug)
    async def create(self) -> str:
        """ Creates the resource in the API with the current params. """
        endpoint = f'{self.base_url}{self.resource_type}'

        self.changed_params = set()

        params = {param: p_value for param, p_value in self.params.copy().items() if p_value is not None}

        for field in self.params_to_serialize:
            if field in params:
                try:
                    params[field] = json.dumps(params[field])
                except TypeError:
                    log_error(logger, f"Field {field} is not serializable", TypeError)

        params = {k: v for k, v in params.items() if v is not None}

        obj = await (
            self.api_client.query_element(
                method='POST', endpoint=endpoint,
                **{'body_params': params}
            )
        )

        for k, v in obj.items():
            if k in self.params:
                if v is None or k not in self.params_to_serialize:
                    self.params[k] = v
                else:
                    try:
                        self.params[k] = json.loads(v)
                    except TypeError:
                        log_error(logger, f"Field {k} is not deserializable", TypeError)

        return obj['id']

    @logging_before_and_after(logging_level=logger.debug)
    async def update(self):
        """ Updates the resource in the API with the current params. """
        endpoint = f'{self.base_url}{self.resource_type}/{self.id}'

        params = {k: v for k, v in self.params.items() if k in self.changed_params}

        for field in self.params_to_serialize:
            if field in params:
                params[field] = json.dumps(params[field])

            assert isinstance(self.params[field], (dict, list))

        if params:
            await(
                self.api_client.query_element(
                    method='PATCH', endpoint=endpoint,
                    **{'body_params': params}
                )
            )
        else:
            logger.debug(f'No params to update for {self.resource_type} {str(self)}')

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
    async def create_children_batch(
        self, resource_class: Type[IsResource], children_params: List[Dict],
        unit: str, batch_size: int = 100
    ):
        """ Creates a batch of children of a given resource class. It doesn't return the created resources,
        And it doesn't save them in the cache.
        :param resource_class: The class of the resource to create.
        :param children_params: The parameters of the resources to create.
        :param unit: The unit of the progress bar.
        :param batch_size: The size of the batch to create.
        """
        if batch_size >= 1000:
            raise ValueError('batch_size must be less than 1000')

        endpoint = f'{self.base_url}{self.resource_type}/{self.id}/{resource_class.resource_type}/batch'

        log_level = logger.getEffectiveLevel()
        disable = log_level > logging.INFO or len(children_params) < 1000

        # TODO Seems to be converted in the api when returned? Solve in local server if that is the case
        if self.api_client.playground:
            # TODO maybe params_to_serialize should be a class attribute
            mock_resource = resource_class(parent=self.wrapper_class_instance)
            for child_params in children_params:
                for field in mock_resource.params_to_serialize:
                    if field in child_params:
                        child_params[field] = json.dumps(child_params[field])

        if not disable:
            logger.info("Uploading data")

        with tqdm(total=len(children_params), unit=unit, disable=disable) \
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

        logger.info("data uploaded") if not disable else None

    @logging_before_and_after(logging_level=logger.debug)
    async def create_child(
            self, resource_class: Type[IsResource], **kwargs
    ) -> IsResource:
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
    async def update_child(
        self, resource_class: Type[IsResource],
        uuid: Optional[str] = None, alias: Optional[Alias] = None,
        **params
    ) -> bool:
        """ Updates a child of a given resource class.
        :param resource_class: The class of the resource to update.
        :param uuid: The uuid of the resource to update.
        :param alias: The alias of the resource to update.
        :param params: The parameters of the resource to update.
        :return: True if the resource was updated, False otherwise.
        """
        return await self.children[resource_class].update(uuid=uuid, alias=alias, **params)

    @logging_before_and_after(logging_level=logger.debug)
    async def get_children(
            self, resource_class: Type[IsResource], limit: Optional[int] = None
    ) -> List[IsResource]:
        """ Gets all children of a given resource class.
        :param resource_class: The class of the resources to get.
        :param limit: The maximum number of resources to get.
        :return: A list of resources.
        """
        return await self.children[resource_class].list(limit)

    @logging_before_and_after(logging_level=logger.debug)
    async def get_child(
            self, resource_class: Type[IsResource],
            uuid: Optional[str] = None, alias: Optional[Alias] = None,
            create_if_not_exists: bool = False
    ) -> Optional[IsResource]:
        """ Gets a child resource.
        :param resource_class: The class of the resource to get.
        :param uuid: The uuid of the resource to get.
        :param alias: The alias of the resource to get.
        :param create_if_not_exists: If True, creates the resource if it does not exist.
        """
        if not uuid and alias is None:
            log_error(logger, f"Cannot get child without uuid or alias", ValueError)

        res_cache: ResourceCache = self.children[resource_class]

        child = await res_cache.get(uuid, alias)

        if not child and alias and create_if_not_exists:
            child = await self.create_child(resource_class, alias=alias)

        return child

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_child(
        self, resource_class: Type[IsResource],
        uuid: Optional[str] = None, alias: Optional[Alias] = None
    ) -> bool:
        """ Deletes a child resource.
        :param resource_class: The class of the resource to delete.
        :param uuid: The uuid of the resource to delete.
        :param alias: The alias of the resource to delete.
        """
        return await self.children[resource_class].delete(uuid, alias)

    @logging_before_and_after(logging_level=logger.debug)
    def clear(self):
        """ Clears the cache. """
        for resource_cache in self.children.values():
            resource_cache.clear()

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

    def __str__(self):
        """ Returns a string representation of the resource. """
        alias = self.get_alias()
        return self.id if not alias else alias

    def __eq__(self, other):
        """ Returns True if the resource is equal to another resource. """
        return self.params == other.params


class Resource(ABC):
    alias_field: Optional[AliasField] = None
    resource_type: Optional[str] = None
    plural: Optional[str] = None
    elastic_supported: bool = False

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(
            self, parent: Optional[IsResource] = None,
            uuid: Optional[str] = None,
            db_resource: Optional[dict[str, Any]] = None,
            api_client: Optional[ApiClient] = None,
            params: Optional[dict[str, Any]] = None,
            children: Optional[List[Type[IsResource]]] = None,
            check_params_before_creation: Optional[List[str]] = None,
            params_to_serialize: Optional[List[str]] = None,
            await_children: Optional[bool] = False
    ):
        """ Initializes a resource. """

        if db_resource:
            uuid = db_resource['id']
        else:
            db_resource = {}

        self._base_resource = BaseResource(
            api_client=api_client, uuid=uuid, parent=parent, params=params,
            resource_type=self.resource_type, alias_field=self.alias_field,
            params_to_serialize=params_to_serialize, await_children=await_children,
            wrapper_class_instance=self
        )

        self._base_resource.children = {
            res_class: ResourceCache(res_class, self) for res_class in children
        } if children else {}

        self._check_params_before_creation = check_params_before_creation if check_params_before_creation else []
        self.api_client: ApiClient = self._base_resource.api_client
        self.parent = self._base_resource.parent
        self.params_to_serialize = self._base_resource.params_to_serialize

        for field, value in db_resource.items():
            if field in self:
                if field in self.params_to_serialize and value is not None:
                    value = json.loads(value)
                self[field] = value

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

    @logging_before_and_after(logging_level=logger.debug)
    def clear(self):
        """ Clears the resource. """
        self._base_resource.clear()

    @logging_before_and_after(logging_level=logger.debug)
    def set_params(self, **kwargs):
        """ Sets the parameters of the resource. """
        for key, value in kwargs.items():
            if isinstance(key, tuple) and len(key) == 2 and isinstance(key[0], str) and isinstance(key[1], str):
                self[key[0]][key[1]] = value
            elif value is not None:
                self[key] = value

    @logging_before_and_after(logging_level=logger.debug)
    def empty_changed_params(self):
        """ Empties the changed_params set. """
        self._base_resource.changed_params = set()

    @logging_before_and_after(logging_level=logger.debug)
    def get_alias_from_other_params(self, params: dict) -> Optional[str]:
        """ Returns the alias of the resource based on the given parameters. """
        return self._base_resource.get_alias(params)

    def __getitem__(self, item):
        """ Returns the value of the parameter with the given name. """
        if item == 'id':
            return self._base_resource.id
        elif item == 'base_url':
            return self._base_resource.base_url
        elif item == 'alias':
            return self._base_resource.get_alias()
        elif item in self._base_resource.params:
            result = self._base_resource.params[item]
            if isinstance(result, (dict, list)):
                self._base_resource.changed_params.add(item)
            return result
        elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str) and isinstance(item[1], str) and \
                item[0] in self._base_resource.params:
            deeper_params = self._base_resource.params[item[0]]
            if item[1] not in deeper_params:
                log_error(logger, f"{self.__class__.__name__} {item[0]} does not contain {item[1]}", KeyError)
            return deeper_params[item[1]]
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
        self._base_resource.params[key] = value if value is not None else class_type()
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

    def __eq__(self, other: IsResource):
        """ Returns whether the resource is equal to another resource. """
        return self._base_resource.__eq__(other._base_resource)
