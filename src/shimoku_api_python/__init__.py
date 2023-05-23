from __future__ import absolute_import
from typing import Dict, Optional

import shimoku_api_python.async_execution_pool
from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext

from shimoku_api_python.api.universe_metadata_api import UniverseMetadataApi, Universe
from shimoku_api_python.api.business_metadata_api import BusinessMetadataApi, Business
from shimoku_api_python.api.dashboard_metadata_api import DashboardMetadataApi, Dashboard
from shimoku_api_python.api.app_metadata_api import AppMetadataApi, App
from shimoku_api_python.api.app_type_metadata_api import AppTypeMetadataApi
from shimoku_api_python.api.report_metadata_api import ReportMetadataApi
from shimoku_api_python.api.data_managing_api import DataSetManagingApi
from shimoku_api_python.api.file_metadata_api import FileMetadataApi
from shimoku_api_python.api.plot_api import PlotApi
from shimoku_api_python.api.ai_api import AiAPI
from shimoku_api_python.api.ping_api import PingApi
from shimoku_api_python.api.activity_metadata_api import ActivityMetadataApi

from shimoku_api_python.utils import clean_menu_path

from shimoku_api_python.client import ApiClient
from shimoku_api_python.exceptions import DashboardError, AppError, BusinessError

import shimoku_components_catalog.html_components

import logging
from shimoku_api_python.execution_logger import configure_logging, logging_before_and_after, log_error
logger = logging.getLogger(__name__)


class Client(object):

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(
        self, universe_id: str, environment: str = 'production',
        access_token: str = '', config: Optional[Dict] = None,
        verbosity: str = None, async_execution: bool = False
    ):
        if not config:
            config = {}

        self.configure_logging = configure_logging
        if verbosity:
            self.configure_logging(verbosity)

        if access_token and access_token != "":
            config = {'access_token': access_token}

        self._api_client = ApiClient(config=config, environment=environment)

        self._universe_object = Universe(self._api_client, uuid=universe_id)
        self._business_object: Optional[Business] = None
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
        self.data = DataSetManagingApi(self._app_object, self.epc)
        self.io = FileMetadataApi(self._app_object, self.epc)
        self.activity = ActivityMetadataApi(self._app_object, self.epc)
        self.plt = PlotApi(self._app_object, self.epc)
        self._reuse_data_sets = False
        self._shared_dfs = {}
        self._shared_custom_data = {}

        self.epc.current_app = self._app_object
        self.epc.universe = self._universe_object

        self.ai = AiAPI(None)
        self.html_components = shimoku_components_catalog.html_components

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def set_business(self, uuid: str, name: str = None):
        """Set business id for the client.
        :param uuid: Business uuid
        :param name: Business name
        """
        if self._business_object:
            self._business_object.currently_in_use = False
        business: Optional[Business] = await self._universe_object.get_business(uuid=uuid, name=name)
        if not business:
            log_error(logger, f'Business {name if name else uuid} not found.', BusinessError)
        self._business_object = business
        self._business_object.currently_in_use = True

        if self._app_object:
            self.plt.raise_if_cant_change_path()
            self._app_object.currently_in_use = False
        self._app_object = None
        if self._dashboard_object:
            self._dashboard_object.currently_in_use = False
        self._dashboard_object = None

        self.dashboard = DashboardMetadataApi(business=business, execution_pool_context=self.epc)
        self.app = AppMetadataApi(business=business, execution_pool_context=self.epc)
        self.report = ReportMetadataApi(app=None, execution_pool_context=self.epc)
        self.activity = ActivityMetadataApi(app=None, execution_pool_context=self.epc)
        self.plt = PlotApi(app=None, execution_pool_context=self.epc)
        self.data = DataSetManagingApi(app=None, execution_pool_context=self.epc)
        self.io = FileMetadataApi(app=None, execution_pool_context=self.epc)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def set_dashboard(self, name: str):
        """Set the dashboard in use for the following apps being called.
        :param name: Dashboard name
        """
        if self._app_object:
            log_error(logger,
                      "A Dashboard can not be set when using an app. Please pop out of the app first.", DashboardError)
        if self._dashboard_object:
            self._dashboard_object.currently_in_use = False
        self._dashboard_object: Dashboard = await self._business_object.get_dashboard(name=name)
        self._dashboard_object.currently_in_use = True

    @logging_before_and_after(logging_level=logger.info)
    def reuse_data_sets(self):
        """ Reuse data sets from the api. """
        self._reuse_data_sets = True
        if self._app_object:
            self.plt.reuse_data_sets = True

    @logging_before_and_after(logging_level=logger.info)
    def update_data_sets(self):
        """ Update data sets in the api. """
        self._reuse_data_sets = False
        if self._app_object:
            self.plt.reuse_data_sets = False

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.debug)
    async def _change_app(self, menu_path: str):
        """Change app in use for the following calls.
        :param menu_path: Menu path of the app
        """
        if self._app_object:
            self._app_object.currently_in_use = False
        app: App = await self._business_object.get_app(menu_path=menu_path)
        self._app_object = app
        app.currently_in_use = True
        self.activity = ActivityMetadataApi(self._app_object, self.epc)
        self.report = ReportMetadataApi(self._app_object, self.epc)
        self.plt = PlotApi(self._app_object, self.epc, self._reuse_data_sets)
        self.data = DataSetManagingApi(self._app_object, self.epc)
        self.io = FileMetadataApi(self._app_object, self.epc)

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
        data_names = []
        if self._app_object:
            self.plt.raise_if_cant_change_path()
            if self._app_object['name'] == app_name:
                self.plt.change_path(path)
                return
            data_names = self.plt.get_shared_data_names()
        self._change_app(menu_path)
        self.plt.change_path(path)
        if data_names:
            logger.info(f'Shared data entries will no longer be available: {data_names}, set them again if needed.')

    @logging_before_and_after(logging_level=logger.info)
    def pop_out_of_menu_path(self):
        """ Pop out of the menu path. """
        self.run()
        if not self._app_object:
            log_error(logger, 'No app is currently in use.', AppError)
        self.plt.raise_if_cant_change_path()
        data_names = self.plt.get_shared_data_names()
        if data_names:
            logger.info(f'Shared data entries will no longer be available: {data_names}, set them again if needed.')
        self._app_object.currently_in_use = False
        self._app_object = None

    @logging_before_and_after(logging_level=logger.info)
    def set_config(self, config: Dict):
        self._api_client.set_config(config)

    @async_auto_call_manager(execute=True)
    async def run(self):
        """ Execute all async calls in the execution pool. """
        pass

    def activate_async_execution(self):
        """ Activate async execution of the tasks. """
        self.epc.sequential = False

    def activate_sequential_execution(self):
        """ Activate sequential execution of the tasks. """
        self.epc.sequential = True

    def get_api_calls_counter(self):
        """ Get the number of api calls made. """
        return self._api_client.call_counter

    def __getattribute__(self, item):
        """ Get attribute of the client. """
        if item in ['dashboard', 'app'] and not self._business_object:
            log_error(logger, 'Business not set. Please use set_business() method first.', AttributeError)
        if item in ['activity', 'plt', 'report', 'data', 'io'] and not self._app_object:
            log_error(logger, 'App not set. Please use set_menu_path() method first.', AttributeError)
        return object.__getattribute__(self, item)
