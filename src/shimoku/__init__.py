from __future__ import absolute_import

from typing import Dict, Optional

from shimoku.async_execution_pool import (
    AutoAsyncExecutionPool,
    decorate_class_to_auto_async,
)

from shimoku.api.client import ApiClient
from shimoku.api.user_access_classes.universes_layer import UniversesLayer, Universe
from shimoku.api.user_access_classes.generated_headers.UniversesLayerHeader import (
    UniversesLayerHeader,
)
from shimoku.api.user_access_classes.businesses_layer import WorkspacesLayer, Business
from shimoku.api.user_access_classes.generated_headers.WorkspacesLayerHeader import (
    WorkspacesLayerHeader,
)
from shimoku.api.user_access_classes.activity_templates_layer import (
    ActivityTemplatesLayer,
)
from shimoku.api.user_access_classes.generated_headers.ActivityTemplatesLayerHeader import (
    ActivityTemplatesLayerHeader,
)
from shimoku.api.user_access_classes.dashboards_layer import BoardsLayer, Dashboard
from shimoku.api.user_access_classes.generated_headers.BoardsLayerHeader import (
    BoardsLayerHeader,
)
from shimoku.api.user_access_classes.apps_layer import MenuPathsLayer, App
from shimoku.api.user_access_classes.generated_headers.MenuPathsLayerHeader import (
    MenuPathsLayerHeader,
)
from shimoku.api.user_access_classes.reports_layer import ComponentsLayer
from shimoku.api.user_access_classes.generated_headers.ComponentsLayerHeader import (
    ComponentsLayerHeader,
)
from shimoku.api.user_access_classes.data_sets_layer import DataSetsLayer
from shimoku.api.user_access_classes.generated_headers.DataSetsLayerHeader import (
    DataSetsLayerHeader,
)
from shimoku.api.user_access_classes.files_layer import FilesLayer
from shimoku.api.user_access_classes.generated_headers.FilesLayerHeader import (
    FilesLayerHeader,
)
from shimoku.api.user_access_classes.activities_layer import ActivitiesLayer
from shimoku.api.user_access_classes.generated_headers.ActivitiesLayerHeader import (
    ActivitiesLayerHeader,
)
from shimoku.api.user_access_classes.actions_layer import ActionsLayer
from shimoku.api.user_access_classes.generated_headers.ActionsLayerHeader import (
    ActionsLayerHeader,
)
from shimoku.plt.plt_layer import PlotLayer
from shimoku.plt.generated_headers.PlotLayerHeader import PlotLayerHeader
from shimoku.plt.utils import create_normalized_name

from shimoku.ai.ai_layer import AILayer
from shimoku.ai.generated_headers.AILayerHeader import AILayerHeader

from shimoku.utils import IN_BROWSER, EventType

from shimoku.exceptions import WorkspaceError, BoardError

import shimoku_components_catalog.html_components

import logging
from shimoku.execution_logger import (
    log_error,
    configure_logging,
    logging_before_and_after,
)

logger = logging.getLogger(__name__)


class Client:
    def __init__(
        self,
        universe_id: str = "local",
        environment: str = "production",
        access_token: Optional[str] = None,
        config: Optional[Dict] = None,
        verbosity: str = None,
        async_execution: bool = False,
        local_port: int = 8000,
        retry_attempts: int = 5,
    ):
        self.playground: bool = universe_id == "local" and not access_token
        if self.playground:
            access_token = "local"
        if universe_id == "local" and not self.playground:
            log_error(
                logger,
                "Local universe can only be used in playground mode.",
                AttributeError,
            )
        self.access_token = access_token
        self.environment = environment
        self._access_token = access_token
        self.universe_id = universe_id
        self.workspace_id = None
        self.board_id = None
        self.menu_path_id = None
        if not config:
            config = {}

        self.server_host = "127.0.0.1"
        self.local_port = local_port

        self.configure_logging = configure_logging
        if verbosity:
            self.configure_logging(verbosity)

        if access_token and access_token != "":
            config = {"access_token": access_token}

        self._api_client = ApiClient(
            config=config,
            environment=environment,
            playground=self.playground,
            server_host=self.server_host,
            server_port=local_port,
            retry_attempts=retry_attempts,
        )

        self._universe_object = Universe(self._api_client, uuid=universe_id)
        self._business_object: Optional[Business] = None
        self._app_object: Optional[App] = None
        self._dashboard_object: Optional[Dashboard] = None

        self._async_pool = AutoAsyncExecutionPool(api_client=self._api_client)

        if async_execution:
            self.activate_async_execution()
        else:
            self.activate_sequential_execution()

        self.universes: UniversesLayerHeader = decorate_class_to_auto_async(
            UniversesLayer, self._async_pool
        )(self._api_client)
        self.workspaces: WorkspacesLayerHeader = decorate_class_to_auto_async(
            WorkspacesLayer, self._async_pool
        )(self._universe_object)
        self.activity_templates: ActivityTemplatesLayerHeader = (
            decorate_class_to_auto_async(ActivityTemplatesLayer, self._async_pool)(
                self._universe_object
            )
        )
        self.actions: ActionsLayerHeader = decorate_class_to_auto_async(
            ActionsLayer, self._async_pool
        )(self._universe_object)
        self.boards: BoardsLayerHeader = decorate_class_to_auto_async(
            BoardsLayer, self._async_pool
        )(self._business_object)
        self.menu_paths: MenuPathsLayerHeader = decorate_class_to_auto_async(
            MenuPathsLayer, self._async_pool
        )(self._business_object)
        self.components: ComponentsLayerHeader = decorate_class_to_auto_async(
            ComponentsLayer, self._async_pool
        )(self._app_object)
        self.data: DataSetsLayerHeader = decorate_class_to_auto_async(
            DataSetsLayer, self._async_pool
        )(self._app_object)
        self.io: FilesLayerHeader = decorate_class_to_auto_async(
            FilesLayer, self._async_pool
        )(self._app_object)
        self.activities: ActivitiesLayerHeader = decorate_class_to_auto_async(
            ActivitiesLayer, self._async_pool
        )(self._app_object)
        self.ai: AILayerHeader = decorate_class_to_auto_async(
            AILayer, self._async_pool
        )(self.access_token, self._universe_object, self._app_object)

        self._reuse_data_sets = False
        self._shared_dfs = {}
        self._shared_custom_data = {}
        self.plt: PlotLayerHeader = decorate_class_to_auto_async(
            PlotLayer, self._async_pool
        )(self._async_pool, self._app_object, self._reuse_data_sets)

        self._async_pool.current_app = self._app_object
        self._async_pool.universe = self._universe_object

        self.html_components = shimoku_components_catalog.html_components

    def set_workspace(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> None:
        """Set workspace id for the client.
        :param uuid: Workspace uuid
        :param name: Workspace name
        """
        if self._api_client.playground:
            uuid, name = "local", None

        @logging_before_and_after(logging_level=logger.info, name="set_workspace")
        async def a_set_workspace(_self):
            if self._business_object:
                self._business_object.currently_in_use = False
            business: Optional[Business] = await self._universe_object.get_business(
                uuid=uuid, name=name
            )
            if not business:
                log_error(
                    logger,
                    f"Workspace {name if name else uuid} not found.",
                    WorkspaceError,
                )
            self._business_object = business
            self._business_object.currently_in_use = True
            self.workspace_id = self._business_object["id"]

            if self._app_object:
                self.plt.raise_if_cant_change_path()
                self._app_object.currently_in_use = False
            self._app_object = None
            self.menu_path_id = None
            if self._dashboard_object:
                self._dashboard_object.currently_in_use = False
            self._dashboard_object = None
            self.board_id = None

            self.boards.__init__(self._business_object)
            self.menu_paths.__init__(self._business_object)
            self.components.__init__(self._app_object)
            self.activities.__init__(self._app_object)
            self.plt.__init__(self._async_pool, self._app_object, self._reuse_data_sets)
            self.data.__init__(self._app_object)
            self.io.__init__(self._app_object)
            self.ai.__init__(self.access_token, self._universe_object, self._app_object)

        return self._async_pool.auto_async_func_call(
            name="set_workspace",
            func_self=self,
            func=a_set_workspace,
        )

    def pop_out_of_menu_path(self) -> None:
        """Pop out of the menu path."""

        @logging_before_and_after(
            logging_level=logger.info, name="pop_out_of_menu_path"
        )
        async def a_pop_out_of_menu_path(_self):
            data_names = self.plt.get_shared_data_names()
            if data_names:
                logger.info(
                    f"Shared data entries will no longer be available: {data_names}, set them again if needed."
                )
            self.plt.clear_context()
            self._app_object.currently_in_use = False
            self._app_object = None
            self.menu_path_id = None

        return self._async_pool.auto_async_func_call(
            name="pop_out_of_menu_path",
            func_self=self,
            func=a_pop_out_of_menu_path,
        )

    def set_board(self, name: str) -> None:
        """Set the board in use for the following apps being called.
        :param name: board name
        """
        if not self._business_object:
            log_error(
                logger,
                "Workspace not set. Please use set_workspace() method first.",
                AttributeError,
            )
        if self._app_object:
            self.pop_out_of_menu_path()
        if self._dashboard_object:
            self._dashboard_object.currently_in_use = False

        @logging_before_and_after(logging_level=logger.info, name="set_board")
        async def a_set_board(_self):
            self._dashboard_object = await self._business_object.get_dashboard(
                name=name
            )
            self._dashboard_object.currently_in_use = True
            self.board_id = self._dashboard_object["id"]

        return self._async_pool.auto_async_func_call(
            name="set_board",
            func_self=self,
            func=a_set_board,
        )

    def pop_out_of_board(self) -> None:
        """Pop out of the dashboard."""
        if not self._business_object:
            log_error(
                logger,
                "Workspace not set. Please use set_workspace() method first.",
                AttributeError,
            )
        if not self._dashboard_object:
            log_error(
                logger,
                "Board not set. Please use set_board() method first.",
                BoardError,
            )
        if self._app_object:
            self.pop_out_of_menu_path()

        @logging_before_and_after(logging_level=logger.info, name="pop_out_of_board")
        async def a_pop_out_of_board(_self):
            self._dashboard_object.currently_in_use = False
            self._dashboard_object = None
            self.board_id = None

        return self._async_pool.auto_async_func_call(
            name="pop_out_of_board",
            func_self=self,
            func=a_pop_out_of_board,
        )

    def enable_caching(self):
        """Enable caching."""
        self._api_client.cache_enabled = True

    def disable_caching(self):
        """Disable caching."""
        self._api_client.cache_enabled = False

    def reuse_data_sets(self):
        """Reuse data sets from the api."""
        self._reuse_data_sets = True
        if self._app_object:
            self.plt.reuse_data_sets = True

    def update_data_sets(self):
        """Update data sets in the api."""
        self._reuse_data_sets = False
        if self._app_object:
            self.plt.reuse_data_sets = False

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
        self.activities.__init__(self._app_object)
        self.components.__init__(self._app_object)
        self.plt.__init__(self._async_pool, self._app_object, self._reuse_data_sets)
        self.data.__init__(self._app_object)
        self.io.__init__(self._app_object)
        self.ai.__init__(self.access_token, self._universe_object, self._app_object)

        self.menu_path_id = self._app_object["id"]

        if dont_add_to_dashboard:
            return

        if not self._dashboard_object:
            self._dashboard_object = await self._business_object.get_dashboard(
                name="Default Name"
            )

        if self._app_object["id"] not in await self._dashboard_object.list_app_ids():
            await self._dashboard_object.insert_app(self._app_object)

        self.menu_path_id = self._app_object["id"]

    def set_menu_path(
        self,
        name: str,
        sub_path: Optional[str] = None,
        dont_add_to_dashboard: bool = False,
    ) -> None:
        """Set menu path for the client.
        :param name: Menu path
        :param sub_path: Sub path
        :param dont_add_to_dashboard: Whether to add the menu path to the dashboard
        """
        if not self._business_object:
            log_error(
                logger,
                "Workspace not set. Please use set_workspace() method first.",
                AttributeError,
            )
        normalized_name = create_normalized_name(name)
        path = sub_path if sub_path else None
        data_names = []
        if self._app_object:
            self.plt.raise_if_cant_change_path()
            if self._app_object["normalizedName"] == normalized_name:
                self.plt.change_path(path)
                return
            data_names = self.plt.get_shared_data_names()

        @logging_before_and_after(logging_level=logger.info, name="set_menu_path")
        async def a_set_menu_path(_self):
            await self._change_app(name, dont_add_to_dashboard)
            self.plt.change_path(path)
            if data_names:
                logger.info(
                    f"Shared data entries will no longer be available: {data_names}, set them again if needed."
                )

        return self._async_pool.auto_async_func_call(
            name="set_menu_path",
            func_self=self,
            func=a_set_menu_path,
        )

    async def _create_business_contents_updated_event(self):
        """Create a business contents updated event."""
        if not self._business_object:
            return
        await self._business_object.create_event(
            EventType.BUSINESS_CONTENTS_UPDATED, {}, self._business_object["id"]
        )
        logger.info("Business contents updated event created")

    def run(self) -> None:
        """Run the tasks in the execution pool."""

        async def a_run(_self):
            if self._api_client.playground:
                self._async_pool.ending_tasks[
                    "Business_contents_updated"
                ] = self._create_business_contents_updated_event()

        return self._async_pool.auto_async_func_call(
            name="run",
            func_self=self,
            func=a_run,
        )

    def activate_async_execution(self):
        """Activate async execution of the tasks."""
        self._async_pool.sequential = False

    def activate_sequential_execution(self):
        """Activate sequential execution of the tasks."""
        self._async_pool.sequential = True

    def get_api_calls_counter(self):
        """Get the number of api calls made."""
        return self._api_client.call_counter

    def __getattribute__(self, item):
        """Get attribute of the client."""
        if False and not IN_BROWSER:
            if item in ["boards", "menu_paths"] and not self._business_object:
                log_error(
                    logger,
                    "Workspace not set. Please use set_workspace() method first.",
                    AttributeError,
                )
            if (
                item in ["activities", "plt", "components", "data", "io"]
                and not self._app_object
            ):
                log_error(
                    logger,
                    "Menu path not set. Please use set_menu_path() method first.",
                    AttributeError,
                )
        return object.__getattribute__(self, item)
