"""
Used as base Mailchimp:
https://github.com/mailchimp/mailchimp-marketing-python/blob/master/mailchimp_marketing/api_client.py
"""

from typing import Optional, Callable

import datetime
import asyncio

from shimoku.exceptions import APIError
from shimoku.utils import IN_BROWSER
import json
from pkg_resources import get_distribution


import logging
from shimoku.execution_logger import ClassWithLogging, log_error

logger = logging.getLogger(__name__)

SHIMOKU_VERSION_KEY = "python-shimoku-pkg-version"


def get_request_function():
    """Auxiliary function to get the appropriate request function"""
    if IN_BROWSER:
        from pyodide.http import pyfetch

        async def request(
            self: "ApiClient",
            method,
            url,
            query_params,
            headers,
            body,
        ):
            params = dict(
                method=method,
                headers=headers,
                body=body
                if isinstance(body, bytes)
                else json.dumps(body).encode("utf-8"),
                timeout=self.timeout,
                params=query_params,
            )
            if method == "GET":
                del params["body"]
            res = await pyfetch(url, **params)
            if (
                hasattr(res, "headers")
                and "application/json" in res.headers.get("content-type")
            ) or ((hasattr(res, "json")) and not hasattr(res, "read")):
                data = await res.json()
            else:
                data = await res.read()
            if not res.ok:
                self.raise_api_exception(data)
            return data

    else:
        import aiohttp

        async def request(
            self: "ApiClient",
            method,
            url,
            query_params,
            headers,
            body,
        ):
            session_params = {
                "auth": aiohttp.BasicAuth("user", self.api_key)
                if self.is_basic_auth
                else None
            }
            if not session_params["auth"]:
                del session_params["auth"]

            request_options = {
                "method": method,
                "url": url,
                "headers": headers,
                "params": query_params,
                "json": body,
            }
            if not headers:
                del request_options["headers"]
            if not query_params:
                del request_options["params"]
            if not body:
                del request_options["json"]
            elif isinstance(body, bytes):
                request_options["data"] = body
                del request_options["json"]

            async with aiohttp.ClientSession(**session_params) as session:
                async with session.request(**request_options) as res:
                    if (
                        "content-type" in res.headers
                        and "application/json" in res.headers.get("content-type")
                    ):
                        data = await res.json()
                    else:
                        data = await res.read()
                    if not res.ok:
                        self.raise_api_exception(data)
                    return data

    return request


def retry(a_func: Callable, n_retries: int):
    """Auxiliary function to retry a function n_retries times waiting exponentially for each retry"""

    async def wrapper(*args, **kwargs):
        for i in range(n_retries):
            try:
                return await a_func(*args, **kwargs)
            except APIError as e:
                await asyncio.sleep(2**i)
                if i == n_retries - 1:
                    raise e
                logger.warning(f"Error: {e}")

    return wrapper


class ApiClient(ClassWithLogging):
    PRIMITIVE_TYPES = (float, int, bool, bytes, str)

    _module_logger = logger

    def __init__(
        self,
        environment: str,
        playground: bool,
        config=None,
        server_host="127.0.0.1",
        server_port=8000,
        retry_attempts: int = 5,
    ):
        self.cache_enabled = True
        self.environment = environment
        self.playground = playground
        self.retry_attempts = retry_attempts

        if config is None:
            config = {}

        if "production".startswith(environment.lower()):
            self.host = "https://api.shimoku.io/external/v1/"
        elif "develop".startswith(environment.lower()):
            self.host = "https://api.develop.shimoku.io/external/v1/"
        elif environment == "guillermo":
            self.host = "https://wxauh7u2te.execute-api.eu-west-1.amazonaws.com/guillermo/external/v1/"
        else:
            raise ValueError(
                f'The namespace must be either "production" or "develop | '
                f"namespace introduced: {environment}"
            )
        if playground:
            self.host = f"http://{server_host}:{server_port}/external/v1/"

        # semaphor for async api calls
        self.semaphore_limit = 10
        self.semaphore = None

        # DEFAULTS
        # Api key
        self.api_key: str = ""
        self.is_basic_auth: bool = False
        # OAuth
        self.access_token: str = ""
        self.is_oauth: bool = False
        # General
        self.server: str = "invalid-server"
        self.timeout: int = 120

        self.default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Swagger-Codegen/0.0/python",
        }
        self.set_config(config)
        self.call_counter = 0
        # Default vars

    def set_config(self, config={}):
        """Set all config values"""
        # Basic Auth
        self.api_key: str = config["api_key"] if "api_key" in config.keys() else ""
        self.is_basic_auth: bool = self.api_key != ""

        # OAuth
        self.access_token: str = (
            config["access_token"] if "access_token" in config.keys() else ""
        )
        self.is_oauth: bool = self.access_token != ""

        if not self.is_oauth and not self.is_basic_auth:
            raise ValueError("You must provide either an API Key or Access Token")

        # If using Basic auth and no server is provided,
        # attempt to extract it from the api_key directly.
        self.server: str = (
            config["server"] if "server" in config.keys() else "invalid-server"
        )
        if self.server == "invalid-server" and self.is_basic_auth:
            self.server: str = self.get_server_from_api_key(self.api_key)

        self.timeout = config["timeout"] if "timeout" in config.keys() else 120

    async def call_api(
        self,
        resource_path,
        method,
        path_params=None,
        query_params=None,
        header_params=None,
        body=None,
        collection_formats=None,
        limit: Optional[int] = None,
        elastic_supported: bool = False,
        **kwargs,
    ):
        """Create and call the API request with headers, params and others"""
        # header parameters
        header_params = header_params or {}
        header_params.update(self.default_headers)
        if header_params:
            header_params = self.sanitize_for_serialization(header_params)
            header_params = dict(
                self.parameters_to_tuples(header_params, collection_formats)
            )

        # path parameters
        if path_params:
            path_params = self.sanitize_for_serialization(path_params)
            path_params = self.parameters_to_tuples(path_params, collection_formats)
            for k, v in path_params:
                # specified safe chars, encode everything
                resource_path = resource_path.replace("{%s}" % k, str(v))

        # query parameters
        if query_params:
            query_params = self.sanitize_for_serialization(query_params)
            query_params = self.parameters_to_tuples(query_params, collection_formats)

        # request url
        url = self.host + resource_path

        if self.server:
            url = url.replace("server", self.server)

        # perform request and return response
        async with self.semaphore:
            return await self.request(
                method,
                url,
                query_params,
                headers=header_params,
                body=body,
                limit=limit,
                elastic_supported=elastic_supported,
            )

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
        for key, val in params["kwargs"].items():
            params[key] = val
        body_params = params["kwargs"].get("data")
        del params["kwargs"]

        collection_formats = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        # HTTP header `Accept`
        header_params["Accept"] = self.select_header_accept(
            ["application/json", "application/problem+json"]
        )  # noqa: E501

        # HTTP header `Content-Type`
        header_params["Content-Type"] = self.select_header_content_type(  # noqa: E501
            ["application/json"]
        )  # noqa: E501

        # Authentication setting
        auth_settings = ["basicAuth"]  # noqa: E501

        return (
            query_params,
            header_params,
            kwargs.get("body_params"),
            form_params,
            local_var_files,
            auth_settings,
            params,
            collection_formats,
        )

    async def query_element(
        self,
        method: str,
        endpoint: str,
        limit: Optional[int] = None,
        elastic_supported: bool = False,
        **kwargs,
    ) -> dict:
        """Retrieve an element if the endpoint exists

        :param method: examples are 'GET', 'POST', etc
        :param endpoint: example: 'business/{businessId}/app/{appId}
        :param limit: limit the number of results returned
        :param elastic_supported: whether the endpoint supports elastic search
        """
        (
            query_params,
            header_params,
            body_params,
            form_params,
            local_var_files,
            auth_settings,
            params,
            collection_formats,
        ) = self.set_http_info(**kwargs)

        path_params = {}
        if endpoint in params:
            path_params[endpoint] = params[endpoint]  # noqa: E501

        element_data: dict = await retry(self.call_api, n_retries=self.retry_attempts)(
            endpoint,
            method,
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
            async_req=params.get("async_req"),
            _return_http_data_only=params.get("_return_http_data_only"),
            _preload_content=params.get("_preload_content", True),
            _request_timeout=params.get("_request_timeout"),
            collection_formats=collection_formats,
        )

        if kwargs.get("progress_bar"):
            progress_bar, how_much = kwargs.get("progress_bar")
            if progress_bar:
                progress_bar.update(how_much)

        return element_data

    @staticmethod
    def raise_api_exception(response: str) -> None:
        """Raise an ApiClientError with the message changed to be more user friendly
        :param response: the response from the API
        """
        replace_words = {
            "report": "component",
            "app": "menu path",
            "business": "workspace",
            "dashboard": "board",
        }
        for word, replacement in replace_words.items():
            response = (
                response.replace(word, replacement)
                if isinstance(response, str)
                else response
            )
        log_error(logger, response, APIError)

    _request = get_request_function()

    async def request(
        self,
        method,
        url,
        query_params=None,
        headers=None,
        body=None,
        limit: Optional[int] = None,
        elastic_supported: bool = False,
        to_tazawa: bool = True,
    ):
        headers = headers or {}
        if to_tazawa:
            headers.update({"Authorization": "Bearer " + self.access_token})
            headers.update(
                {
                    SHIMOKU_VERSION_KEY: get_distribution("shimoku").version
                    if not IN_BROWSER
                    else "2.0.0"
                }
            )

        if method not in ["GET", "HEAD", "OPTIONS", "DELETE", "POST", "PUT", "PATCH"]:
            raise ValueError(
                "http method must be `GET`, `HEAD`, `OPTIONS`,"
                " `POST`, `PATCH`, `PUT` or `DELETE`."
            )
        body_from = 0
        next_token = None
        data_res = {} if not elastic_supported else []
        req_limit = limit if limit else 100
        method = method if not elastic_supported else "POST"

        while True:  # loop until nextToken is None
            aux_url = url
            if to_tazawa:
                if elastic_supported:
                    body = {"from": body_from, "limit": req_limit}
                elif method == "GET":
                    aux_url += (
                        f"?nextToken={next_token}"
                        if next_token
                        else f"?limit={req_limit}"
                    )

            logger.debug(
                f"method:{method}, url: {aux_url}, headers: {headers},"
                f"query params: {query_params}, body: {body}"
            )

            data = await self._request(
                method=method,
                url=aux_url,
                query_params=query_params,
                headers=headers,
                body=body,
            )
            self.call_counter += 1
            logger.debug(data)

            if not to_tazawa:
                return data

            if elastic_supported:
                data_res.extend(data)
                body_from += req_limit
                if limit:
                    limit -= req_limit
                if len(data) < req_limit or (limit and limit <= 0):
                    break
            elif data and "items" in data:
                if data_res.get("items"):
                    data_res["items"].extend(data.get("items"))
                else:
                    data_res = data
                next_token = data.get("nextToken")
                if not next_token:
                    break
            else:
                data_res = data
                break

        return data_res

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
            return [self.sanitize_for_serialization(sub_obj) for sub_obj in obj]
        elif isinstance(obj, tuple):
            return tuple(self.sanitize_for_serialization(sub_obj) for sub_obj in obj)
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

        return {
            key: self.sanitize_for_serialization(val) for key, val in obj_dict.items()
        }

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
        for k, v in (
            params.items() if isinstance(params, dict) else params
        ):  # noqa: E501
            if k in collection_formats:
                collection_format = collection_formats[k]
                if collection_format == "multi":
                    new_params.extend((k, value) for value in v)
                else:
                    if collection_format == "ssv":
                        delimiter = " "
                    elif collection_format == "tsv":
                        delimiter = "\t"
                    elif collection_format == "pipes":
                        delimiter = "|"
                    else:  # csv is the default
                        delimiter = ","
                    new_params.append((k, delimiter.join(str(value) for value in v)))
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

        if "application/json" in accepts:
            return "application/json"
        else:
            return ", ".join(accepts)

    @staticmethod
    def get_server_from_api_key(api_key: str) -> str:
        try:
            split: list[str] = api_key.split("-")
            if len(split) == 2:
                return split[1]
            else:
                return "invalid-server"
        except:
            return ""

    @staticmethod
    def select_header_content_type(content_types):
        """Returns `Content-Type` based on an array of content_types provided.
        :param content_types: List of content-types.
        :return: Content-Type (e.g. application/json).
        """
        if not content_types:
            return "application/json"

        content_types = [x.lower() for x in content_types]

        if "application/json" in content_types or "*/*" in content_types:
            return "application/json"
        else:
            return content_types[0]
