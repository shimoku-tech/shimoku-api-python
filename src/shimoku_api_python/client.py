"""
Used as base Mailchimp:
https://github.com/mailchimp/mailchimp-marketing-python/blob/master/mailchimp_marketing/api_client.py
"""

from typing import List, Dict, Optional

import datetime
import requests
from tenacity import retry, wait_exponential, stop_after_attempt
from shimoku_api_python.exceptions import ApiClientError
from pkg_resources import get_distribution

import aiohttp
import logging
from shimoku_api_python.execution_logger import logging_before_and_after, my_before_sleep

logger = logging.getLogger(__name__)


class ApiClient(object):
    PRIMITIVE_TYPES = (float, int, bool, bytes, str)

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(
        self, environment: str, playground: bool,
        config=None, server_host=None, server_port=None,
        retry_attempts: int = 5
    ):

        self.cache_enabled = True
        self.environment = environment
        self.playground = playground
        self.retry_attempts = retry_attempts

        if config is None:
            config = {}

        if 'production'.startswith(environment.lower()):
            self.host = 'https://api.shimoku.io/external/v1/'
        elif 'develop'.startswith(environment.lower()):
            self.host = 'https://api.develop.shimoku.io/external/v1/'
        elif environment == 'guillermo':
            self.host = 'https://wxauh7u2te.execute-api.eu-west-1.amazonaws.com/guillermo/external/v1/'
        else:
            raise ValueError(
                f'The namespace must be either "production" or "develop | '
                f'namespace introduced: {environment}'
            )
        if playground:
            self.host = f'http://{server_host}:{server_port}/external/v1/'

        # semaphor for async api calls
        self.semaphore_limit = 10
        self.semaphore = None

        # DEFAULTS
        # Api key
        self.api_key: str = ''
        self.is_basic_auth: bool = False
        # OAuth
        self.access_token: str = ''
        self.is_oauth: bool = False
        # General
        self.server: str = 'invalid-server'
        self.timeout: int = 120

        self.default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Swagger-Codegen/0.0/python'
        }
        self.set_config(config)
        self.call_counter = 0

        # Default vars

    @logging_before_and_after(logging_level=logger.debug)
    def set_config(self, config={}):
        """Set all config values"""
        # Basic Auth
        self.api_key: str = config['api_key'] if 'api_key' in config.keys() else ''
        self.is_basic_auth: bool = self.api_key != ''

        # OAuth
        self.access_token: str = config['access_token'] if 'access_token' in config.keys() else ''
        self.is_oauth: bool = self.access_token != ''

        if not self.is_oauth and not self.is_basic_auth:
            raise ValueError('You must provide either an API Key or Access Token')

        # If using Basic auth and no server is provided,
        # attempt to extract it from the api_key directly.
        self.server: str = config['server'] if 'server' in config.keys() else 'invalid-server'
        if self.server == 'invalid-server' and self.is_basic_auth:
            self.server: str = self.get_server_from_api_key(self.api_key)

        self.timeout = config['timeout'] if 'timeout' in config.keys() else 120

    @logging_before_and_after(logging_level=logger.debug)
    async def call_api(
        self, resource_path, method, path_params=None, query_params=None,
        header_params=None, body=None, collection_formats=None, limit: Optional[int] = None,
        elastic_supported: bool = False, **kwargs
    ):
        """Create and call the API request with headers, params and others"""
        # header parameters
        header_params = header_params or {}
        header_params.update(self.default_headers)
        if header_params:
            header_params = self.sanitize_for_serialization(header_params)
            header_params = dict(self.parameters_to_tuples(header_params, collection_formats))

        # path parameters
        if path_params:
            path_params = self.sanitize_for_serialization(path_params)
            path_params = self.parameters_to_tuples(path_params, collection_formats)
            for k, v in path_params:
                # specified safe chars, encode everything
                resource_path = resource_path.replace(
                    '{%s}' % k,
                    str(v)
                )

        # query parameters
        if query_params:
            query_params = self.sanitize_for_serialization(query_params)
            query_params = self.parameters_to_tuples(query_params, collection_formats)

        # request url
        url = self.host + resource_path

        if self.server:
            url = url.replace('server', self.server)

        # perform request and return response
        async with self.semaphore:
            return await self.request(
                method, url, query_params,
                headers=header_params, body=body,
                limit=limit, elastic_supported=elastic_supported
            )

    @logging_before_and_after(logging_level=logger.debug)
    def set_http_info(self, **kwargs):  # noqa: E501
        """
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.remove_with_http_info(campaign_id, async_req=True)
        >>> result = thread.get()
        :param async_req bool
        :param str campaign_id: The unique id for the campaign. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        params = locals()
        for key, val in params['kwargs'].items():
            params[key] = val
        body_params = params['kwargs'].get('data')
        del params['kwargs']

        collection_formats = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        # HTTP header `Accept`
        header_params['Accept'] = self.select_header_accept(
            ['application/json', 'application/problem+json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['basicAuth']  # noqa: E501

        return (
            query_params, header_params,
            kwargs.get('body_params'), form_params, local_var_files,
            auth_settings, params, collection_formats,
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def query_element(
            self, method: str, endpoint: str,
            limit: Optional[int] = None,
            elastic_supported: bool = False,
            **kwargs
    ) -> Dict:
        """Retrieve an element if the endpoint exists

        :param method: examples are 'GET', 'POST', etc
        :param endpoint: example: 'business/{businessId}/app/{appId}
        :param limit: limit the number of results returned
        :param elastic_supported: whether the endpoint supports elastic search
        """
        (
            query_params, header_params,
            body_params, form_params, local_var_files,
            auth_settings, params, collection_formats,
        ) = self.set_http_info(**kwargs)

        path_params = {}
        if endpoint in params:
            path_params[endpoint] = params[endpoint]  # noqa: E501

        element_data: Dict = await (
            retry(stop=stop_after_attempt(self.retry_attempts),
                  wait=wait_exponential(multiplier=2, min=1, max=16),
                  before_sleep=my_before_sleep)(self.call_api)(
                endpoint, method,
                path_params,
                query_params,
                header_params,
                limit=limit,
                elastic_supported=elastic_supported,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=None,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats,
            )
        )

        if kwargs.get('progress_bar'):
            progress_bar, how_much = kwargs.get('progress_bar')
            progress_bar.update(how_much)

        return element_data

    @staticmethod
    @logging_before_and_after(logging_level=logger.debug)
    def raise_api_exception(response: str) -> None:
        """Raise an ApiClientError with the message changed to be more user friendly
        :param response: the response from the API
        """
        replace_words = {
            'report': 'component',
            'app': 'menu path',
            'business': 'workspace',
            'dashboard': 'board',
        }
        for word, replacement in replace_words.items():
            response = response.replace(word, replacement) if isinstance(response, str) else response
        logger.error(response)
        raise ApiClientError(response)

    @logging_before_and_after(logging_level=logger.debug)
    async def request(
        self, method, url,
        query_params=None, headers=None, body=None,
        limit: Optional[int] = None, elastic_supported: bool = False
    ):
        auth = None
        if self.is_basic_auth:
            auth = ('user', self.api_key)

        if self.is_basic_auth:
            auth = aiohttp.BasicAuth('user', self.api_key)
        elif self.is_oauth:
            headers = headers or {}
            headers.update({'Authorization': 'Bearer ' + self.access_token})
            headers.update({'shimoku-api-version': get_distribution("shimoku_api_python").version})

        if method not in ['GET', 'HEAD', 'OPTIONS', 'DELETE', 'POST', 'PUT', 'PATCH']:
            raise ValueError(
                "http method must be `GET`, `HEAD`, `OPTIONS`,"
                " `POST`, `PATCH`, `PUT` or `DELETE`."
            )
        body_from = 0
        next_token = None
        data_res = {} if not elastic_supported else []
        req_limit = limit if limit else 100
        method = method if not elastic_supported else 'POST'
        async with aiohttp.ClientSession(auth=auth, timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:

            while True:  # loop until nextToken is None
                aux_url = url
                if elastic_supported:
                    body = {'from': body_from, 'limit': req_limit}
                elif method == 'GET':
                    aux_url += (f'?nextToken={next_token}' if next_token else f'?limit={req_limit}')

                logger.debug(f'method:{method}, url: {aux_url}, headers: {headers},'
                             f'query params: {query_params}, body: {body}')

                async with session.request(method, aux_url, headers=headers, params=query_params, json=body) as res:
                    self.call_counter += 1
                    try:
                        if 'application/json' in res.headers.get('content-type'):
                            data = await res.json()
                        else:
                            data = await res.text()

                        if not res.ok:
                            self.raise_api_exception(data)
                        logger.debug(data)

                        if elastic_supported:
                            data_res.extend(data)
                            body_from += req_limit
                            if limit:
                                limit -= req_limit
                            if len(data) < req_limit or (limit and limit <= 0):
                                break
                        elif 'items' in data:
                            if data_res.get('items'):
                                data_res['items'].extend(data.get('items'))
                            else:
                                data_res = data
                            next_token = data.get('nextToken')
                            if not next_token:
                                break
                        else:
                            data_res = data
                            next_token = None
                            break

                    except Exception as e:
                        self.raise_api_exception(str(e))

        return data_res

    def raw_request(self, **kwargs):
        return requests.request(**kwargs)

    def sanitize_for_serialization(self, obj):
        """Builds a JSON POST object.
        If obj is None, return None.
        If obj is str, int, long, float, bool, return directly.
        If obj is datetime.datetime, datetime.date
            convert to string in iso8601 format.
        If obj is list, sanitize each element in the list.
        If obj is dict, return the dict.
        If obj is swagger model, return the properties dict.
        :param obj: The data to serialize.
        :return: The serialized form of data.
        """
        if obj is None:
            return None
        elif isinstance(obj, self.PRIMITIVE_TYPES):
            return obj
        elif isinstance(obj, list):
            return [self.sanitize_for_serialization(sub_obj)
                    for sub_obj in obj]
        elif isinstance(obj, tuple):
            return tuple(self.sanitize_for_serialization(sub_obj)
                         for sub_obj in obj)
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        if isinstance(obj, dict):
            obj_dict = obj
        else:
            # Convert model obj to dict except
            # attributes `swagger_types`, `attribute_map`
            # and attributes which value is not None.
            # Convert attribute name to json key in
            # model definition for request.
            obj_dict = {
                obj.attribute_map[attr]: getattr(obj, attr)
                for attr, _ in obj.items()
                if getattr(obj, attr) is not None
            }

        return {key: self.sanitize_for_serialization(val)
                for key, val in obj_dict.items()}

    @staticmethod
    def parameters_to_tuples(params, collection_formats):
        """Get parameters as list of tuples, formatting collections.
        :param params: Parameters as dict or list of two-tuples
        :param dict collection_formats: Parameter collection formats
        :return: Parameters as list of tuples, collections formatted
        """
        new_params = []
        if collection_formats is None:
            collection_formats = {}
        for k, v in params.items() if isinstance(params, dict) else params:  # noqa: E501
            if k in collection_formats:
                collection_format = collection_formats[k]
                if collection_format == 'multi':
                    new_params.extend((k, value) for value in v)
                else:
                    if collection_format == 'ssv':
                        delimiter = ' '
                    elif collection_format == 'tsv':
                        delimiter = '\t'
                    elif collection_format == 'pipes':
                        delimiter = '|'
                    else:  # csv is the default
                        delimiter = ','
                    new_params.append(
                        (k, delimiter.join(str(value) for value in v)))
            else:
                new_params.append((k, v))
        return new_params

    @staticmethod
    def select_header_accept(accepts):
        """Returns `Accept` based on an array of accepts provided.
        :param accepts: List of headers.
        :return: Accept (e.g. application/json).
        """
        if not accepts:
            return

        accepts = [x.lower() for x in accepts]

        if 'application/json' in accepts:
            return 'application/json'
        else:
            return ', '.join(accepts)

    @staticmethod
    def get_server_from_api_key(api_key: str) -> str:
        try:
            split: List[str] = api_key.split('-')
            if len(split) == 2:
                return split[1]
            else:
                return 'invalid-server'
        except:
            return ''

    @staticmethod
    def select_header_content_type(content_types):
        """Returns `Content-Type` based on an array of content_types provided.
        :param content_types: List of content-types.
        :return: Content-Type (e.g. application/json).
        """
        if not content_types:
            return 'application/json'

        content_types = [x.lower() for x in content_types]

        if 'application/json' in content_types or '*/*' in content_types:
            return 'application/json'
        else:
            return content_types[0]
