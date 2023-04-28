from __future__ import absolute_import
from typing import List, Dict, Optional, Union, Tuple, Any, Iterable, Callable


import shimoku_api_python.async_execution_pool
from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext
# import apis into sdk package
from shimoku_api_python.api.universe_metadata_api import UniverseMetadataApi, Universe
from shimoku_api_python.api.business_metadata_api import BusinessMetadataApi, Business
from shimoku_api_python.api.dashboard_metadata_api import DashboardMetadataApi, Dashboard
from shimoku_api_python.api.app_metadata_api import AppMetadataApi, App
from shimoku_api_python.api.app_type_metadata_api import AppTypeMetadataApi
from shimoku_api_python.api.report_metadata_api import ReportMetadataApi
from shimoku_api_python.api.data_managing_api import DataManagingApi
from shimoku_api_python.api.file_metadata_api import FileMetadataApi
from shimoku_api_python.api.plot_api import NewPlotApi
from shimoku_api_python.api.ai_api import AiAPI
from shimoku_api_python.api.ping_api import PingApi
from shimoku_api_python.api.activity_metadata_api import ActivityMetadataApi

from shimoku_api_python.utils import clean_menu_path

from shimoku_api_python.client import ApiClient

import shimoku_components_catalog.html_components
# from shimoku_api_python.configuration import Configuration

import logging
from shimoku_api_python.execution_logger import configure_logging, logging_before_and_after, log_error
logger = logging.getLogger(__name__)


class Client(object):

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, universe_id: str, environment: str = 'production',
                 access_token: str = '', config: Optional[Dict] = None, business_id: str = '',
                 verbosity: str = None, async_execution: bool = False):

        if not config:
            config = {}

        self.configure_logging = configure_logging
        if verbosity:
            self.configure_logging(verbosity)

        if access_token and access_token != "":
            config = {'access_token': access_token}

        self._api_client = ApiClient(
            config=config,
            universe_id=universe_id,
            environment=environment,
        )

        self._universe_object = Universe(self._api_client, uuid=universe_id)
        self._business_object: Optional[Business] = \
            Business(self._universe_object, uuid=business_id) if business_id else None
        self._app_object: Optional[App] = None
        self._dashboard_object: Optional[Dashboard] = None

        self.epc = ExecutionPoolContext(api_client=self._api_client)

        if async_execution:
            self.activate_async_execution()
        else:
            self.activate_sequential_execution()

        self.ping = PingApi(self._api_client)
        self.universe = UniverseMetadataApi(self._api_client, self.epc)
        self.business = BusinessMetadataApi(self._universe_object, self.epc)
        self.dashboard = DashboardMetadataApi(self._business_object, self.epc)
        self.app = AppMetadataApi(self._business_object, self.epc)
        self.report = ReportMetadataApi(self._app_object, self.epc)
        self.data = DataManagingApi(self._api_client)
        self.io = FileMetadataApi(self._api_client, business_id=business_id, execution_pool_context=self.epc)
        self.activity = ActivityMetadataApi(self._app_object, self.epc)
        self.plt = NewPlotApi(self._app_object, self.epc)

        self.epc.plot_api = self.plt
        self.epc.universe = self._universe_object

        self.ai = AiAPI(self.plt)
        self.html_components = shimoku_components_catalog.html_components

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def set_business(self, business_id: str):
        """Set business id for the client.
        :param business_id: Business uuid
        """
        business: Business = await self._universe_object.get_business(uuid=business_id)
        self._business_object = business
        self._app_object = None
        self._dashboard_object = None

        self.dashboard = DashboardMetadataApi(business=business, execution_pool_context=self.epc)
        self.app = AppMetadataApi(business=business, execution_pool_context=self.epc)
        self.report = ReportMetadataApi(app=None, execution_pool_context=self.epc)
        self.activity = ActivityMetadataApi(app=None, execution_pool_context=self.epc)
        self.plt = NewPlotApi(app=None, execution_pool_context=self.epc)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def set_dashboard(self, name: str):
        """Set the dashboard in use for the following apps being called.
        :param name: Dashboard name
        """
        self._dashboard_object: Dashboard = await self._business_object.get_dashboard(name=name)
        app = self._app_object
        if app and app['id'] not in await self._dashboard_object.list_app_ids():
            await self._dashboard_object.insert_app(app)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.debug)
    async def _change_app(self, menu_path: str):
        """Change app in use for the following calls.
        :param menu_path: Menu path of the app
        """
        app: App = await self._business_object.get_app(menu_path=menu_path)
        self._app_object = app
        self.report = ReportMetadataApi(app=app, execution_pool_context=self.epc)
        self.activity = ActivityMetadataApi(app=app, execution_pool_context=self.epc)
        self.plt = NewPlotApi(app=app, execution_pool_context=self.epc)

        self.activity = ActivityMetadataApi(self._app_object, self.epc)
        self.report = ReportMetadataApi(self._app_object, self.epc)
        self.plt = NewPlotApi(self._app_object, self.epc)
        self.epc.plot_api = self.plt

        if not self._dashboard_object:
            self._dashboard_object = await self._business_object.get_dashboard(name='Dashboard')

        if self._app_object['id'] not in await self._dashboard_object.list_app_ids():
            await self._dashboard_object.insert_app(self._app_object)

    @logging_before_and_after(logging_level=logger.info)
    def set_menu_path(self, menu_path: str):
        """Set menu path for the client.
        :param menu_path: Menu path
        """
        app_name, path = clean_menu_path(menu_path)
        if self._app_object:
            self.plt.raise_if_cant_change_path()
            if self._app_object['name'] == app_name:
                self.plt.change_path(path)
                return
        self._change_app(menu_path)
        self.plt.change_path(path)

    @logging_before_and_after(logging_level=logger.info)
    def set_config(self, config: Dict):
        self._api_client.set_config(config)

    @async_auto_call_manager(execute=True)
    async def run(self):
        """ Execute all async calls in the execution pool. """
        pass

    def activate_async_execution(self):
        self.epc.sequential = False

    def activate_sequential_execution(self):
        self.epc.sequential = True

    def __getattribute__(self, item):
        # TODO: uncomment when the refactoring is done
        # if item in ['dashboard', 'app'] and not self._business_object:
        #     log_error(logger, 'Business not set. Please use set_business() method first.', AttributeError)
        # if item in ['activity', 'plt', 'report', 'data', 'io'] and not self._app_object:
        #     log_error(logger, 'App not set. Please use set_menu_path() method first.', AttributeError)
        return object.__getattribute__(self, item)
