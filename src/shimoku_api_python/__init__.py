from __future__ import absolute_import

import shutil
from typing import Dict, Optional

import tempfile
import subprocess
import tqdm

import shimoku_api_python.async_execution_pool
from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext

from shimoku_api_python.api.universe_metadata_api import UniverseMetadataApi, Universe
from shimoku_api_python.api.business_metadata_api import BusinessMetadataApi, Business
from shimoku_api_python.api.activity_template_metadata_api import ActivityTemplateMetadataApi
from shimoku_api_python.api.dashboard_metadata_api import DashboardMetadataApi, Dashboard
from shimoku_api_python.api.app_metadata_api import AppMetadataApi, App
from shimoku_api_python.api.report_metadata_api import ReportMetadataApi
from shimoku_api_python.api.data_managing_api import DataSetManagingApi
from shimoku_api_python.api.file_metadata_api import FileMetadataApi
from shimoku_api_python.api.plot_api import PlotApi
from shimoku_api_python.api.ai_api import AiApi
from shimoku_api_python.api.ping_api import PingApi
from shimoku_api_python.api.activity_metadata_api import ActivityMetadataApi
from shimoku_api_python.websockets_server import EventType

from shimoku_api_python.code_generation.main_code_gen import generate_code

from shimoku_api_python.utils import create_normalized_name, ShimokuPalette, create_function_name

from shimoku_api_python.client import ApiClient
from shimoku_api_python.exceptions import BoardError, MenuPathError, WorkspaceError

from shimoku_api_python.execute_local_server import create_server, kill_server, check_server

import shimoku_components_catalog.html_components

import logging
from shimoku_api_python.execution_logger import configure_logging, logging_before_and_after, log_error

logger = logging.getLogger(__name__)


class Client(object):

    def _set_app_modules(self):
        self.components = ReportMetadataApi(self._app_object, self.epc)
        self.data = DataSetManagingApi(self._app_object, self.epc)
        self.io = FileMetadataApi(self._app_object, self.epc)
        self.activities = ActivityMetadataApi(self._app_object, self.epc)
        self.plt = PlotApi(self._app_object, self.epc)
        self.ai = AiApi(self._access_token, self._universe_object, self._app_object, self.epc)

    def _set_modules(self):
        self.ping = PingApi(self._api_client)
        self.universes = UniverseMetadataApi(self._api_client, self.epc)
        self.workspaces = BusinessMetadataApi(self._universe_object, self.epc)
        self.activity_templates = ActivityTemplateMetadataApi(self._universe_object, self.epc)
        self.boards = DashboardMetadataApi(self._business_object, self.epc)
        self.menu_paths = AppMetadataApi(self._business_object, self.epc)
        self._set_app_modules()

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(
            self, universe_id: str = 'local', environment: str = 'production',
            access_token: Optional[str] = None, config: Optional[Dict] = None,
            verbosity: str = None, async_execution: bool = False,
            local_port: int = 8000, open_browser_for_local_server: bool = False,
            retry_attempts: int = 5
    ):
        self.playground: bool = universe_id == 'local' and not access_token
        if self.playground:
            access_token = 'local'
        if universe_id == 'local' and not self.playground:
            log_error(logger, 'Local universe can only be used in playground mode.', AttributeError)
        self.access_token = access_token
        self.environment = environment
        self._access_token = access_token
        self.universe_id = universe_id
        self.workspace_id = None
        self.board_id = None
        self.menu_path_id = None
        if not config:
            config = {}

        self.server_host = '127.0.0.1'
        self.local_port = local_port
        if self.playground and not check_server(self.server_host, local_port):
            create_server(environment, self.server_host, local_port, open_browser_for_local_server)

        self.configure_logging = configure_logging
        if verbosity:
            self.configure_logging(verbosity)

        if access_token and access_token != "":
            config = {'access_token': access_token}

        self._api_client = ApiClient(
            config=config, environment=environment, playground=self.playground,
            server_host=self.server_host, server_port=local_port, retry_attempts=retry_attempts)

        self._universe_object = Universe(self._api_client, uuid=universe_id)
        self._business_object: Optional[Business] = None
        self._app_object: Optional[App] = None
        self._dashboard_object: Optional[Dashboard] = None

        self.epc = ExecutionPoolContext(api_client=self._api_client)

        if async_execution:
            self.activate_async_execution()
        else:
            self.activate_sequential_execution()

        self._set_modules()

        self._reuse_data_sets = False
        self._shared_dfs = {}
        self._shared_custom_data = {}

        self.epc.current_app = self._app_object
        self.epc.universe = self._universe_object

        self.html_components = shimoku_components_catalog.html_components

    @logging_before_and_after(logging_level=logger.info)
    def terminate_local_server(self):
        kill_server(self.server_host, self.local_port)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def set_workspace(self, uuid: Optional[str] = None, name: Optional[str] = None):
        """Set workspace id for the client.
        :param uuid: Workspace uuid
        :param name: Workspace name
        """
        if self._api_client.playground:
            uuid, name = 'local', None

        if self._business_object:
            self._business_object.currently_in_use = False
        business: Optional[Business] = await self._universe_object.get_business(uuid=uuid, name=name)
        if not business:
            log_error(logger, f'Workspace {name if name else uuid} not found.', WorkspaceError)
        self._business_object = business
        self._business_object.currently_in_use = True
        self.workspace_id = self._business_object['id']

        if self._app_object:
            self.plt.raise_if_cant_change_path()
            self._app_object.currently_in_use = False
        self._app_object = None
        self.menu_path_id = None
        if self._dashboard_object:
            self._dashboard_object.currently_in_use = False
        self._dashboard_object = None
        self.board_id = None

        self._set_modules()

    @logging_before_and_after(logging_level=logger.debug)
    def pop_out_of_menu_path(self):
        """ Pop out of the menu path. """
        self.run()
        data_names = self.plt.get_shared_data_names()
        if data_names:
            logger.info(f'Shared data entries will no longer be available: {data_names}, set them again if needed.')
        self.plt.clear_context()
        self._app_object.currently_in_use = False
        self._app_object = None
        self.menu_path_id = None

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def set_board(self, name: str):
        """Set the board in use for the following apps being called.
        :param name: board name
        """
        if not self._business_object:
            log_error(logger, 'Workspace not set. Please use set_workspace() method first.', AttributeError)
        if self._app_object:
            self.pop_out_of_menu_path()
        if self._dashboard_object:
            self._dashboard_object.currently_in_use = False
        self._dashboard_object: Dashboard = await self._business_object.get_dashboard(name=name)
        self._dashboard_object.currently_in_use = True
        self.board_id = self._dashboard_object['id']

    @logging_before_and_after(logging_level=logger.info)
    def pop_out_of_dashboard(self):
        """ Pop out of the dashboard. """
        if not self._business_object:
            log_error(logger, 'Workspace not set. Please use set_workspace() method first.', AttributeError)
        if not self._dashboard_object:
            log_error(logger, 'Board not set. Please use set_board() method first.', BoardError)
        if self._app_object:
            self.pop_out_of_menu_path()
        self.run()
        self._dashboard_object.currently_in_use = False
        self._dashboard_object = None
        self.board_id = None

    @logging_before_and_after(logging_level=logger.info)
    def enable_caching(self):
        """ Enable caching. """
        self._api_client.cache_enabled = True

    @logging_before_and_after(logging_level=logger.info)
    def disable_caching(self):
        """ Disable caching. """
        self._api_client.cache_enabled = False

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
    async def _change_app(self, menu_path: str, dont_add_to_dashboard: bool):
        """Change app in use for the following calls.
        :param menu_path: Menu path of the app
        :param dont_add_to_dashboard: Whether to add the menu path to the dashboard
        """
        if self._app_object:
            self._app_object.currently_in_use = False

        app: App = await self._business_object.get_app(name=menu_path)
        self._app_object = app
        app.currently_in_use = True

        self._set_app_modules()

        self.menu_path_id = self._app_object['id']

        if dont_add_to_dashboard:
            return

        if not self._dashboard_object:
            self._dashboard_object = await self._business_object.get_dashboard(name='Default Name')

        if self._app_object['id'] not in await self._dashboard_object.list_app_ids():
            await self._dashboard_object.insert_app(self._app_object)

    @logging_before_and_after(logging_level=logger.info)
    def set_menu_path(self, name: str, sub_path: Optional[str] = None, dont_add_to_dashboard: bool = False):
        """Set menu path for the client.
        :param name: Menu path
        :param sub_path: Sub path
        :param dont_add_to_dashboard: Whether to add the menu path to the dashboard
        """
        if not self._business_object:
            log_error(logger, 'Workspace not set. Please use set_workspace() method first.', AttributeError)
        app_name = create_normalized_name(name)
        path = sub_path if sub_path else None
        data_names = []
        if self._app_object:
            self.plt.raise_if_cant_change_path()
            if self._app_object['normalizedName'] == app_name:
                self.plt.change_path(path)
                return
            data_names = self.plt.get_shared_data_names()
        self._change_app(name, dont_add_to_dashboard)
        self.plt.change_path(path)
        if data_names:
            logger.info(f'Shared data entries will no longer be available: {data_names}, set them again if needed.')

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def generate_code(
            self, output_path: str = 'generated_code',
            menu_paths: Optional[list[str]] = None, use_black_formatter: bool = False,
            show_progress_bar: bool = False
    ):
        """ Generate code for a set workspace.
        menu_paths: List of menu paths to generate code from, if None all menu paths are used.
        """
        if not self._business_object:
            log_error(logger, 'Workspace not set. Please use set_workspace() method first.', AttributeError)
        pbar = None
        if show_progress_bar:
            pbar = tqdm.tqdm(total=sum([len(await app.get_reports())
                                        for app in await self._business_object.get_apps()]) + 1)
        await generate_code(
            business_object=self._business_object,
            business_id=self.workspace_id,
            access_token=self._api_client.access_token,
            universe_id=self.universe_id,
            environment=self._api_client.environment,
            output_path=output_path,
            menu_paths=menu_paths,
            epc=self.epc,
            use_black_formatter=use_black_formatter,
            pbar=pbar
        )
        if pbar:
            pbar.close()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def commit_contents_to(
            self, access_token: str,
            universe_id: str, workspace_id: str,
            environment: str = 'production',
            show_progress_bar: bool = True
    ):
        """ Commit contents to another workspace.
        :param access_token: access token to use
        :param universe_id: universe id to use
        :param workspace_id: workspace id to use
        :param environment: environment to use
        :param show_progress_bar: whether to show progress bar
        """
        if not self._business_object:
            log_error(logger, 'Workspace not set. Please use set_workspace() method first.', AttributeError)
        temp_dir = tempfile.mkdtemp()
        pbar = None
        if show_progress_bar:
            pbar = tqdm.tqdm(total=sum([len(await app.get_reports())
                                        for app in await self._business_object.get_apps()]) + 1)
        await generate_code(
            business_object=self._business_object,
            business_id=workspace_id,
            access_token=access_token,
            universe_id=universe_id,
            environment=environment,
            output_path=temp_dir,
            menu_paths=None,
            epc=self.epc,
            use_black_formatter=False,
            pbar=pbar
        )
        if pbar:
            pbar.close()
        process = subprocess.run(
            ['python', f'{temp_dir}/execute_workspace_{create_function_name(self._business_object["name"])}.py'],
            check=True
        )
        if process.returncode != 0:
            log_error(logger, 'Error while executing the generated code.', RuntimeError)
        shutil.rmtree(temp_dir)

    @logging_before_and_after(logging_level=logger.info)
    def pull_contents_from(
            self, access_token: str,
            universe_id: str, workspace_id: str,
            environment: str = 'production',
            show_progress_bar: bool = True
    ):
        """ Pull contents from another workspace.
        :param access_token: access token to use
        :param universe_id: universe id to use
        :param workspace_id: workspace id to use
        :param environment: environment to use
        :param show_progress_bar: whether to show progress bar
        """
        aux_shimoku_client = Client(
            access_token=access_token,
            universe_id=universe_id,
            environment=environment,
        )
        aux_shimoku_client.set_workspace(workspace_id)

        aux_shimoku_client.commit_contents_to(
            access_token=self._api_client.access_token,
            universe_id=self.universe_id,
            workspace_id=self.workspace_id,
            environment=self._api_client.environment,
            show_progress_bar=show_progress_bar
        )

    @logging_before_and_after(logging_level=logger.info)
    def set_config(self, config: Dict):
        self._api_client.set_config(config)

    @logging_before_and_after(logging_level=logger.debug)
    async def _create_business_contents_updated_event(self):
        """ Create a business contents updated event. """
        await self._business_object.create_event(
            EventType.BUSINESS_CONTENTS_UPDATED, {}, self._business_object['id']
        )
        logger.info('Business contents updated event created')

    @async_auto_call_manager(execute=True)
    async def run(self):
        """ Execute all async calls in the execution pool. """
        if self._api_client.playground:
            self.epc.ending_tasks['Business_contents_updated'] = self._create_business_contents_updated_event()
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
        if item in ['boards', 'menu_paths'] and not self._business_object:
            log_error(logger, 'Workspace not set. Please use set_workspace() method first.', AttributeError)
        if item in ['activities', 'plt', 'components', 'data', 'io'] and not self._app_object:
            log_error(logger, 'Menu path not set. Please use set_menu_path() method first.', AttributeError)
        return object.__getattribute__(self, item)
