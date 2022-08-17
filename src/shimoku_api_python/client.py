"""
Used as base Mailchimp:
https://github.com/mailchimp/mailchimp-marketing-python/blob/master/mailchimp_marketing/api_client.py
"""


from typing import List, Dict

import datetime
import requests
import json

from shimoku_api_python.exceptions import ApiClientError


class ApiClient(object):
    PRIMITIVE_TYPES = (float, int, bool, bytes, str)

    def __init__(self, universe_id: str, environment: str, config={}):
        if environment == 'production':
            self.host = 'https://api.shimoku.io/external/v1/'
        elif environment == 'staging':
            self.host = 'https://api.staging.shimoku.io/external/v1/'
        elif environment == 'develop':
            self.host = 'https://api.develop.shimoku.io/external/v1/'
        else:
            raise ValueError(
                f'The namespace must be either "production", "staging" or "develop | '
                f'namespace introduced: {environment}'
            )

        self.host: str = f'{self.host}universe/{universe_id}/'

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

        # Default vars

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

    def call_api(
            self, resource_path, method, path_params=None, query_params=None,
            header_params=None, body=None, collection_formats=None, **kwargs
    ):
        """Create and call the API request with headers, params and others"""
        # header parameters
        header_params = header_params or {}
        header_params.update(self.default_headers)
        if header_params:
            header_params = self.sanitize_for_serialization(header_params)
            header_params = dict(self.parameters_to_tuples(header_params,
                                                           collection_formats))

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
        try:
            res = self.request(
                method, url, query_params,
                headers=header_params, body=body,
            )
        except Exception as err:
            raise ApiClientError(err)

        try:
            if 'application/json' in res.headers.get('content-type'):
                data = res.json()
            else:
                data = res.text
        except Exception:
            data = None

        if res.ok:
            return data
        else:
            raise ApiClientError(data)

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

    def query_element(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict:
        """Retrieve an element if the endpoint exists

        :param method: examples are 'GET', 'POST', etc
        :param endpoint: example: 'business/{businessId}/app/{appId}
        """
        (
            query_params, header_params,
            body_params, form_params, local_var_files,
            auth_settings, params, collection_formats,
        ) = self.set_http_info(**kwargs)

        path_params = {}
        if endpoint in params:
            path_params[endpoint] = params[endpoint]  # noqa: E501

        element_data: Dict = (
            self.call_api(
                endpoint, method,
                path_params,
                query_params,
                header_params,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=None,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats
            )
        )
        return element_data

    def request(self, method, url, query_params=None, headers=None, body=None):
        auth = None

        if self.is_basic_auth:
            auth = ('user', self.api_key)

        if self.is_oauth:
            if headers:
                headers.update({'Authorization': 'Bearer ' + self.access_token})
            else:
                headers = {'Authorization': 'Bearer ' + self.access_token}

        if method == "GET":
            return requests.get(
                url, params=query_params, headers=headers,
                auth=auth, timeout=self.timeout
            )
        elif method == "HEAD":
            return requests.head(
                url, params=query_params, headers=headers,
                auth=auth, timeout=self.timeout
            )
        elif method == "OPTIONS":
            return requests.options(
                url, params=query_params, headers=headers,
                auth=auth, timeout=self.timeout
            )
        elif method == "POST":
            return requests.post(
                url, data=json.dumps(body), params=query_params,
                headers=headers, auth=auth, timeout=self.timeout
            )
        elif method == "PUT":
            return requests.put(
                url, data=json.dumps(body), params=query_params,
                headers=headers, auth=auth, timeout=self.timeout
            )
        elif method == "PATCH":
            return requests.patch(
                url, data=json.dumps(body), params=query_params,
                headers=headers, auth=auth, timeout=self.timeout
            )
        elif method == "DELETE":
            return requests.delete(
                url, params=query_params, headers=headers,
                auth=auth, timeout=self.timeout
            )
        else:
            raise ValueError(
                "http method must be `GET`, `HEAD`, `OPTIONS`,"
                " `POST`, `PATCH`, `PUT` or `DELETE`."
            )

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
