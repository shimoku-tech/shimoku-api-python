import inspect
import json

from shimoku_api_python.websockets_server import Subscription, define_event_method

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import uuid
import datetime as dt
from typing import List, Optional, Any, Dict
from copy import copy

from starlette_graphene3 import GraphQLApp, make_graphiql_handler
import graphene

from dataclasses import asdict
import schema_classes
import schema_parameter_classses
from inspect import getmembers, isclass
import aiohttp

print_paths = True


def now_time_format():
    """
    Get the current time in the format that the API expects
    """
    return dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def get_resource_name(_type, to_lower=True):
    """
    Get the resource name from the type
    :param _type: The type to get the resource name from
    :param to_lower: Whether to return the resource name with the first letter lowercased
    """
    cut = _type[:-7]
    if to_lower:
        cut = cut[0].lower() + cut[1:]
    # Ends with 'Exposed'
    return cut


def get_plural(parents_url_singular):
    """
    Get the plural of a parent url
    :param parents_url_singular: The singular of the parent url
    """
    if parents_url_singular in ['Data', 'data', 'business']:
        return parents_url_singular
    elif parents_url_singular.endswith('s'):
        return parents_url_singular + 'es'
    elif parents_url_singular.endswith('y'):
        return parents_url_singular[:-1] + 'ies'
    else:
        return parents_url_singular + 's'


def get_query_field(types: Dict[str, Any], db: Dict[str, Any], element_type: str):
    """
    Generate a graphql get query field for a given type
    :param types: a dictionary of all the types
    :param db: the database
    :param element_type: the type to generate the query field for
    """

    element_id_param = get_resource_name(element_type) + 'Id' \
        if element_type not in ['AccountExposed', 'UserExposed'] else 'id'

    def resolver(self, info, **kwargs):
        return db[element_type][kwargs[element_id_param]]

    return graphene.Field(
        types[element_type],
        **{element_id_param: graphene.ID(required=True)},
        resolver=resolver
    )


def list_query_field(types: Dict[str, Any], db: Dict[str, Any], parent_type: str, element_type: str):
    """
    Generate a graphql list query field for a given type
    :param types: a dictionary of all the types
    :param db: the database
    :param parent_type: the type of the parent
    :param element_type: the type to generate the query field for
    """

    parent_id_param = get_resource_name(parent_type) + 'Id'
    query_params = {
        parent_id_param: graphene.ID(required=True),
        'limit': graphene.Int(),
        'from': graphene.Int(name='from')
    }
    list_resolver_extra = None
    if hasattr(types[element_type], 'list_resolver_extra'):
        list_resolver_extra = types[element_type].list_resolver_extra

        annotations = inspect.getfullargspec(list_resolver_extra).annotations

        for arg_name, arg_type in annotations.items():
            if arg_name not in ['args', 'kwargs', 'return']:
                query_params[arg_name] = graphene.Argument(types[arg_type])

    def resolver(self, info, **kwargs):
        results = copy(getattr(db[parent_type][str(kwargs[parent_id_param])],
                       get_plural(get_resource_name(element_type))))
        results.items = copy(results.items)
        if list_resolver_extra is not None:
            results.items = list_resolver_extra(items=results.items, **kwargs)
        if 'from' in kwargs:
            results.items = results.items[kwargs['from']:]
        if 'limit' in kwargs:
            results.items = results.items[:kwargs['limit']]
        return results

    return graphene.Field(
        types[element_type + 'List'],
        **query_params,
        resolver=resolver
    )


def generate_schema(fast_api_app, types, db, is_child_of):
    query_fields = {}
    for type_name, type_class in types.items():
        if not type_name.endswith('Exposed') or 'Filtered' in type_name or 'Input' in type_name:
            continue
        name = 'get' + get_resource_name(type_name, to_lower=False)
        query_fields[name] = get_query_field(types, db, type_name)

        if type_name in is_child_of:
            parent_type = is_child_of[type_name]
            name = 'list' + get_plural(get_resource_name(type_name, to_lower=False))
            query_fields[name] = list_query_field(types, db, parent_type, type_name)

    Query = type("Query", (graphene.ObjectType,), query_fields)
    schema = graphene.Schema(query=Query, subscription=Subscription)

    # Integrate with FastAPI (assuming you have a way to do this)
    graphql_app = GraphQLApp(schema, on_get=make_graphiql_handler())
    fast_api_app.add_route("/graphql", graphql_app)
    fast_api_app.add_websocket_route("/graphql", graphql_app)


def get_children(types: Dict[str, Any]):
    """
    Generate a dictionaries of all the children and parents of the exposed types
    :param types: a dictionary of all the types
    """
    is_child_of = {}
    is_parent_of = {}
    links = {}
    for type_name, type_class in types.items():
        if 'Exposed' not in type_name or 'Filtered' in type_name:
            continue
        for field_name, field_def in type_class.__dict__.items():
            if not hasattr(field_def, '_type'):
                continue
            field_type = field_def.type

            if not hasattr(field_type, 'items'):
                element_type_name = field_type.__name__
                links[(type_name, field_name)] = element_type_name
            else:
                # is_child_of[element_type_name] = (type_name, field_name)
                element_type_name = field_type.items.of_type.__name__
                is_child_of[element_type_name] = type_name
                if type_name not in is_parent_of:
                    is_parent_of[type_name] = []
                is_parent_of[type_name].append(element_type_name)

    return is_child_of, is_parent_of


def clean_element(types: Dict[str, Any], element_type: str, element: Any):
    """
    Clean an element to be sent to the frontend or SDK
    :param types: a dictionary of all the types
    :param element_type: The type of the element
    :param element: The element to clean
    """
    dict_rep = {}
    for field_name, field_type in types[element_type].__dict__.items():
        if isinstance(field_type, (graphene.List, graphene.Field)) or field_name.startswith('_'):
            continue
        first_upper = field_name[0].upper() + field_name[1:] + 'Exposed'
        if first_upper in types:
            dict_rep[field_name + 'Id'] = getattr(element, field_name).id \
                if hasattr(getattr(element, field_name), 'id') else None
        dict_rep[field_name] = getattr(element, field_name)

    return dict_rep


async def list_elements(
        types: Dict[str, Any], db: Dict[str, Any], is_child_of: Dict[str, str], parent0Id: str, element_type: str
) -> List[Dict[str, Any]]:
    """
    List all elements of a given type and parent id
    :param types: a dictionary of all the types
    :param db: the database
    :param is_child_of: a dictionary of the parents of the exposed types
    :param parent0Id: The id of the parent element
    :param element_type: The type of the element
    """
    if parent0Id is not None:
        parent_type = is_child_of[element_type]
        if parent0Id not in db[parent_type]:
            raise HTTPException(status_code=404, detail=f'{element_type} with id {parent0Id} not found')
        parent0 = db[parent_type][parent0Id]
        if getattr(parent0, get_plural(get_resource_name(element_type))) is None:
            return []
        return [clean_element(types, element_type, copy(elm))
                for elm in getattr(parent0, get_plural(get_resource_name(element_type))).items]

    return [clean_element(types, element_type, copy(elm)) for elm in db[element_type].values()]


def set_parent(parent_type: str, parent0Id: str, input_class: type, element_type: str, params: dict):
    """
    Set the parent of the element to be created
    :param parent_type: The type of the parent
    :param parent0Id: The id of the parent
    :param input_class: The class of the input
    :param element_type: The type of the element
    :param params: The parameters of the element
    """
    parent_id_key = f'{get_resource_name(parent_type)}Id'
    alternative_parent_id_key = f'{get_resource_name(element_type)}{get_resource_name(parent_type, False)}Id'
    if hasattr(input_class, parent_id_key):
        params[parent_id_key] = parent0Id
    elif hasattr(input_class, alternative_parent_id_key):
        params[alternative_parent_id_key] = parent0Id


def set_children_and_links(types: Dict[str, Any], db: Dict[str, Any], element_type: str, params: dict):
    """
    Set the children and links of the element to be created
    :param types: a dictionary of all the types
    :param db: the database
    :param element_type: The type of the element
    :param params: The parameters of the element
    """
    for field_name, field_def in types[element_type].__dict__.items():
        if field_name.startswith('_'):
            continue
        if isinstance(field_def, graphene.Field) and hasattr(field_def.type, 'items'):
            params[field_name] = field_def.type(items=[])
            if hasattr(params[field_name], 'total'):
                params[field_name].total = 0
        elif field_name + 'Id' in params and params[field_name + 'Id'] is not None:
            field_name_id = field_name + 'Id'
            link_type_name = field_name[0].upper() + field_name[1:]
            link_type_name = link_type_name + 'Exposed'
            link_id = params[field_name_id]
            if link_type_name in types:
                if link_id not in db[link_type_name]:
                    raise HTTPException(status_code=404, detail=f'{link_type_name} with id {link_id} not found')
                if not hasattr(types[element_type], field_name_id):
                    del params[field_name_id]
                params[field_name] = db[link_type_name][link_id]
            else:
                raise HTTPException(status_code=404, detail=f'{link_type_name} not found in types')


def append_to_parent(
        db: Dict[str, Any], element_id: str, parent_type: str, parent0Id: str, element_type: str
):
    """
    Append the element to the parent
    :param db: the database
    :param element_id: The id of the element
    :param parent_type: The type of the parent
    :param parent0Id: The id of the parent
    :param element_type: The type of the element
    """
    plural_name = get_plural(get_resource_name(element_type))
    list_field = getattr(db[parent_type][parent0Id], plural_name)
    if list_field.items is None:
        print('BAD')
    list_field.items.append(db[element_type][element_id])
    if hasattr(list_field, 'total'):
        list_field.total = (list_field.total if list_field.total else 0) + 1


def set_contained_classes(types: Dict[str, Any], element_type: str, params: dict):
    for k, v in params.items():
        if not hasattr(types[element_type], k):
            continue
        linked_type = getattr(types[element_type], k)
        if not hasattr(linked_type, '__name__'):
            continue
        type_of_contained_class_name = getattr(types[element_type], k).__name__
        if type_of_contained_class_name in types:
            if v is not None:
                params[k] = types[type_of_contained_class_name](**v)


async def create_element(
        types: Dict[str, Any], db: Dict[str, Any], is_child_of: Dict[str, str],
        parent0Id: str, element_type: str, params: Any, input_class: type
) -> Dict[str, Any]:
    """
    Create an element of type element_type
    :param types: a dictionary of all the types
    :param db: the database
    :param is_child_of: a dictionary of the parents of the exposed types
    :param parent0Id: The id of the parent
    :param element_type: The type of the element
    :param params: The parameters of the element
    :param input_class: The class of the input
    """
    parent_type = is_child_of[element_type]
    if parent0Id not in db[parent_type]:
        raise HTTPException(status_code=404, detail=f'{element_type} with id {parent0Id} not found')

    created_at = now_time_format()
    if not isinstance(params, dict):
        params = asdict(params)

    _id = str(uuid.uuid4())
    params.update({'id': _id})

    if hasattr(types[element_type], 'createdAt'):
        params['createdAt'] = created_at

    set_contained_classes(types, element_type, params)
    set_parent(parent_type, parent0Id, input_class, element_type, params)
    set_children_and_links(types, db, element_type, params)

    if element_type not in db:
        db[element_type] = {}

    aux_params = {}
    for key, value in params.items():
        if hasattr(types[element_type], key):
            aux_params[key] = value
    params = aux_params

    db[element_type][_id] = types[element_type](**params)

    append_to_parent(db, _id, parent_type, parent0Id, element_type)

    return clean_element(types, element_type, db[element_type][_id])


async def update_element(types: Dict[str, Any], db: Dict[str, Any], element_type: str, Id: str, params: Any):
    """
    Update an element of type element_type
    :param types: a dictionary of all the types
    :param db: the database
    :param element_type: The type of the element
    :param Id: The id of the element
    :param params: The parameters to update
    """
    if Id not in db[element_type]:
        raise HTTPException(status_code=404, detail=f'{element_type} with id {Id} not found')
    params = asdict(params)
    for key, value in params.items():
        if value is not None:
            setattr(db[element_type][Id], key, value)

    return clean_element(types, element_type, db[element_type][Id])


async def delete_r(db: Dict[str, Any], is_parent_of: Dict[str, List[str]], delete_type: str, delete_id: str):
    """
    Delete an element of type delete_type and all its children
    :param db: the database
    :param is_parent_of: a dictionary of the children of the exposed types
    :param delete_type: The type of the element
    :param delete_id: The id of the element
    """
    if delete_id not in db[delete_type]:
        return
    if delete_type in is_parent_of:
        for child_type in is_parent_of[delete_type]:
            plural = get_plural(get_resource_name(child_type))
            plural = plural[0].lower() + plural[1:]
            children_to_delete = getattr(db[delete_type][delete_id], plural)
            if children_to_delete is None:
                continue
            for child in children_to_delete.items:
                if getattr(child, 'id'):
                    await delete_r(db, is_parent_of, child_type, getattr(child, 'id'))
    del db[delete_type][delete_id]


async def delete_element(
        db: Dict[str, Any], is_child_of: Dict[str, str], is_parent_of: Dict[str, List[str]],
        parent0Id: str, element_type: str, Id: str
):
    """
    Delete an element of type element_type
    :param db: the database
    :param is_child_of: a dictionary of the parents of the exposed types
    :param is_parent_of: a dictionary of the children of the exposed types
    :param parent0Id: The id of the parent
    :param element_type: The type of the element
    :param Id: The id of the element
    """
    parent_type = is_child_of[element_type]
    plural_name = get_plural(get_resource_name(element_type))
    parent_children = getattr(db[parent_type][parent0Id], plural_name)
    parent_children.items = [elm for elm in getattr(db[parent_type][parent0Id], plural_name).items if elm.id != Id]
    if hasattr(parent_children, 'total'):
        parent_children.total = parent_children.total - 1
    if Id not in db[element_type]:
        raise HTTPException(status_code=404, detail=f'{element_type} with id {Id} not found')
    await delete_r(db, is_parent_of, element_type, Id)
    return {"message": "Deleted"}


def define_get_method(
        fast_api_app: FastAPI, types: Dict[str, Any], db: Dict[str, Any], parents_url: str, element_type: str
):
    """
    Define the GET method for the element
    :param fast_api_app: The fast api app
    :param types: a dictionary of all the types
    :param db: the database
    :param parents_url: The url of the parent
    :param element_type: The type of the element
    """
    print('GET ' + parents_url + '/{Id}') if print_paths else None

    @fast_api_app.get(parents_url + '/{Id}')
    async def get(Id: str):
        return clean_element(types, element_type, db[element_type][Id])


def define_list_method(
        fast_api_app: FastAPI, types: Dict[str, Any], db: Dict[str, Any],
        is_child_of: Dict[str, str], parents_url: str, element_type: str
):
    """
    Define the GET method for the list of elements
    :param fast_api_app: The fast api app
    :param types: a dictionary of all the types
    :param db: the database
    :param is_child_of: a dictionary of the parents of the exposed types
    :param parents_url: The url of the parent
    :param element_type: The type of the element
    """
    print('GET ' + get_plural(parents_url)) if print_paths else None

    @fast_api_app.get(get_plural(parents_url))
    async def list_elms(parent0Id: Optional[str] = None):
        return await list_elements(types, db, is_child_of, parent0Id, element_type)

    @fast_api_app.post(get_plural(parents_url))
    async def list_elms(parent0Id: Optional[str] = None):
        return await list_elements(types, db, is_child_of, parent0Id, element_type)


def define_create_method(
        fast_api_app: FastAPI, types: Dict[str, Any], db: Dict[str, Any], is_child_of: Dict[str, str],
        parents_url: str, element_type: str, uppercase_type_name: str,
):
    """
    Define the POST method for the element if the input class exists
    :param fast_api_app: The fast api app
    :param types: a dictionary of all the types
    :param db: the database
    :param is_child_of: a dictionary of the parents of the exposed types
    :param parents_url: The url of the parent
    :param element_type: The type of the element
    :param uppercase_type_name: The name of the type of the element with the first letter in uppercase
    """
    create_input_name = 'Create' + uppercase_type_name + 'Input'
    if create_input_name in types:
        input_class = types[create_input_name]
        print('POST ' + parents_url) if print_paths else None

        @fast_api_app.post(parents_url)
        async def _create(parent0Id: Optional[str], params: input_class):
            return await create_element(types, db, is_child_of, parent0Id, element_type, params, input_class)


def define_batch_create_method(
        fast_api_app: FastAPI, types: Dict[str, Any], db: Dict[str, Any], is_child_of: Dict[str, str],
        parents_url: str, element_type: str, uppercase_type_name: str,
):
    """
    Define the POST method for the batch creation of elements if the input class exists
    :param fast_api_app: The fast api app
    :param types: a dictionary of all the types
    :param db: the database
    :param is_child_of: a dictionary of the parents of the exposed types
    :param parents_url: The url of the parent
    :param element_type: The type of the element
    :param uppercase_type_name: The name of the type of the element with the first letter in uppercase
    """
    batch_create_input_name = 'BatchCreate' + uppercase_type_name + 'Input'
    if batch_create_input_name in types:
        print('POST ' + parents_url + '/batch') if print_paths else None

        @fast_api_app.post(parents_url + '/batch')
        async def batch_create(parent0Id: Optional[str], request: Request):
            items = await request.json()
            if not isinstance(items, list):
                raise HTTPException(status_code=400, detail=f'Expected a list of {batch_create_input_name}')
            #TODO: Get a more generic name for the input class
            for item in items:
                await create_element(types, db, is_child_of, parent0Id, element_type, item, types['CreateDataInput'])
            return {'result': 'ok'}


def define_update_method(
        fast_api_app: FastAPI, types: Dict[str, Any], db: Dict[str, Any],
        parents_url: str, element_type: str, uppercase_type_name: str
):
    """
    Define the PATCH method for the element if the input class exists
    :param fast_api_app: The fast api app
    :param types: a dictionary of all the types
    :param db: the database
    :param parents_url: The url of the parent
    :param element_type: The type of the element
    :param uppercase_type_name: The name of the type of the element with the first letter in uppercase
    """
    update_input_name = 'Update' + uppercase_type_name + 'Input'
    if update_input_name in types:
        input_class = types[update_input_name]
        print('PATCH ' + parents_url + '/{Id}') if print_paths else None

        @fast_api_app.patch(parents_url + "/{Id}")
        async def update(Id: str, params: input_class):
            return await update_element(types, db, element_type, Id, params)


def define_delete_method(
        fast_api_app: FastAPI, types: Dict[str, Any], db: Dict[str, Any], is_child_of: Dict[str, Any],
        is_parent_of: Dict[str, Any], parents_url: str, element_type: str, uppercase_type_name: str
):
    """
    Define the DELETE method for the element if the input class exists
    :param fast_api_app: The fast api app
    :param types: a dictionary of all the types
    :param db: the database
    :param is_child_of: a dictionary of the parents of the exposed types
    :param is_parent_of: a dictionary of the children of the exposed types
    :param parents_url: The url of the parent
    :param element_type: The type of the element
    :param uppercase_type_name: The name of the type of the element with the first letter in uppercase
    """
    delete_input_name = 'Delete' + uppercase_type_name + 'Input'
    if delete_input_name in types:
        print('DELETE ' + parents_url + '/{Id}') if print_paths else None

        @fast_api_app.delete(parents_url + "/{Id}")
        async def delete(parent0Id: str, Id: str):
            return await delete_element(db, is_child_of, is_parent_of, parent0Id, element_type, Id)


def generate_crud_methods(
        fast_api_app: FastAPI, types: Dict[str, Any], db: Dict[str, Any],
        is_child_of: Dict[str, str], is_parent_of: Dict[str, List[str]], element_type: str
):
    """
    Generate the CRUD methods for the element
    :param fast_api_app: the fast api app
    :param types: a dictionary of all the types
    :param db: the database
    :param is_child_of: a dictionary of the parents of the exposed types
    :param is_parent_of: a dictionary of the children of the exposed types
    :param element_type: The type of the element
    """
    base_url = '/external/v1/'

    aux_type = element_type
    parents_url = ''
    parent_index = 0
    while aux_type in is_child_of:
        parent_type = is_child_of[aux_type]
        parents_url = get_resource_name(parent_type) + '/{parent' + str(parent_index) + 'Id}/' + parents_url
        aux_type = parent_type
        parent_index += 1

    parents_url = base_url + parents_url + get_resource_name(element_type)

    uppercased_type_name = element_type[:-7]

    define_get_method(fast_api_app, types, db, parents_url, element_type)
    define_list_method(fast_api_app, types, db, is_child_of, parents_url, element_type)
    define_create_method(fast_api_app, types, db, is_child_of, parents_url, element_type, uppercased_type_name)
    define_batch_create_method(fast_api_app, types, db, is_child_of, parents_url, element_type, uppercased_type_name)
    define_update_method(fast_api_app, types, db, parents_url, element_type, uppercased_type_name)
    define_delete_method(fast_api_app, types, db, is_child_of, is_parent_of,
                         parents_url, element_type, uppercased_type_name)


def define_webhook_methods(fast_api_app: FastAPI, types: Dict[str, Any], db: Dict[str, Any]):
    """
    Define the methods for the webhooks, these cant be created with the generate_crud_methods function
    because the pattern is different
    :param fast_api_app: the fast api app
    :param types: a dictionary of all the types
    :param db: the database
    """
    CreateWebhookInput = types['CreateActivityWebHookInput']

    @fast_api_app.post("/external/v1/universe/{parent3Id}/business/{parent2Id}/app/{parent1Id}/"
                       "activity/{parent0Id}/webhook")
    async def create(parent0Id: str, params: CreateWebhookInput):
        webhook_class = types['ActivityWebHookExposed']
        params = asdict(params)
        params.update({
            'id': str(uuid.uuid4()),
            'activity': db['ActivityExposed'][parent0Id],
            'createdAt': now_time_format(),
            'updatedAt': now_time_format(),
            'activityId': parent0Id,
        })
        db['ActivityExposed'][parent0Id].webhook = webhook_class(**params)
        return clean_element(types, 'ActivityWebHookExposed', db['ActivityExposed'][parent0Id].webhook)

    @fast_api_app.post("/external/v1/universe/{parent4Id}/business/{parent3Id}/app/{parent2Id}/activity/{parent1Id}/"
                       "run/{parent0Id}/triggerWebhook")
    async def call_webhook(parent4Id: str, parent3Id: str, parent2Id: str, parent1Id: str, parent0Id: str):
        if db['ActivityExposed'][parent1Id].webhook is None:
            raise HTTPException(status_code=404, detail=f'Webhook not found')

        webhook = db['ActivityExposed'][parent1Id].webhook
        headers = webhook.headers
        if headers is None:
            headers = {}
        else:
            headers = json.loads(headers)
        body = {
            'runId': parent0Id,
            'activityId': parent1Id,
            'appId': parent2Id,
            'businessId': parent3Id,
            'universeId': parent4Id,
        }
        url = webhook.url
        method = webhook.method

        db['RunExposed'][parent0Id].isWebhookCalled = True

        if db['RunExposed'][parent0Id].logs is None:
            db['RunExposed'][parent0Id].logs = []

        db['RunExposed'][parent0Id].logs.items.append(types['LogExposed'](
            id=str(uuid.uuid4()),
            dateTime=now_time_format(),
            message='Process started',
            runId=parent0Id,
            run=db['RunExposed'][parent0Id],
            severity='INFO',
        ))

        # async call to webhook with aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=json.dumps(body)) as response:
                await response.text()

        return {'STATUS': 'OK'}


def create_api() -> FastAPI:
    """
    Create the API with FastAPI and Strawberry
    """
    types = {c[0]: c[1] for c in getmembers(schema_classes, isclass)}
    types.update({c[0]: c[1] for c in getmembers(schema_parameter_classses, isclass)})

    # Add the fields that cannot be added in the class definition
    for type_name, type_class in types.items():
        if hasattr(type_class, 'add_fields'):
            types[type_name] = type_class.add_fields()

    active_universe_plan = types['ActiveUniversePlan'](
        id='local', planType=types['PlanType'](id='local', limits=None, price=None, type=None)
    )
    db = {
        'UniverseFilteredExposed': {
            'local': types['UniverseFilteredExposed'](id='local', name='local', activeUniversePlanId='local',
            activeUniversePlan=active_universe_plan)
        },
        'UniverseExposed': {
            'local': types['UniverseExposed'](id='local', name='local', activeUniversePlanId='local',
            activeUniversePlan=active_universe_plan)
        },
        'BusinessExposed': {
            'local': types['BusinessExposed'](id='local', name='local', type='local', createdAt='2021-01-01'),
        },
    }
    db['UniverseExposed']['local'].business = types['BusinessExposedList'](items=[db['BusinessExposed']['local']])
    db['UniverseFilteredExposed']['local'].business = types['BusinessExposedList'](items=[db['BusinessExposed']['local']])
    db['UniverseExposed']['local'].modules = types['ModuleExposedList'](items=[])
    db['UniverseFilteredExposed']['local'].modules = types['ModuleExposedList'](items=[])
    db['BusinessExposed']['local'].apps = types['AppExposedList'](items=[], total=0)
    db['BusinessExposed']['local'].dashboards = types['DashboardExposedList'](items=[], total=0)
    db['BusinessExposed']['local'].rolePermissions = types['RolePermissionExposedList'](items=[])
    db['BusinessExposed']['local'].modules = types['ModuleExposedList'](items=[])
    db['BusinessExposed']['local'].universe = db['UniverseFilteredExposed']['local']
    db['AccountExposed'] = {
        'local': types['AccountExposed'](id='local', business=db['BusinessExposed']['local'])
    }

    fast_api_app = FastAPI()

    is_child_of, is_parent_of = get_children(types)

    generate_schema(fast_api_app, types, db, is_child_of)

    # Generate the CRUD methods for each type and define the webhook methods
    for _type in types:
        if _type in is_child_of:
            generate_crud_methods(fast_api_app, types, db, is_child_of, is_parent_of, _type)

    define_webhook_methods(fast_api_app, types, db)
    define_event_method(fast_api_app)

    return fast_api_app


# Create the API
app = create_api()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    server_host = "127.0.0.1"
    server_port = 8000
    uvicorn.run(app, host=server_host, port=server_port)


if __name__ == "__main__":
    main()
