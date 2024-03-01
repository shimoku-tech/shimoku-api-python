from shimoku.async_execution_pool import AutoAsyncExecutionPool

# TODO fix this file
from shimoku.api.resources.universe import Universe
from shimoku.api.resources.business import Business
from shimoku.api.resources.app import App
from shimoku.api.resources.dashboard import Dashboard

import shimoku_components_catalog.html_components

from typing import Optional, Dict, List, Union
from uuid import uuid4
from shimoku import Client

import logging
from shimoku.execution_logger import configure_logging

logger = logging.getLogger(__name__)


class MockApiClient:
    """Mock Api Client class"""

    semaphore_limit = 10
    call_counter = 0
    cache_enabled = True
    playground = False

    async def query_element(
        self, method: str, endpoint: str, limit: Optional[int] = None, **kwargs
    ) -> Union[Dict, List, bool]:
        """MOCK. Retrieve an element if the endpoint exists

        :param method: examples are 'GET', 'POST', etc
        :param endpoint: example: 'business/{businessId}/app/{appId}
        :param limit: limit the number of results returned
        """
        body_params = kwargs.get("body_params", {})
        if isinstance(body_params, list) and method == "POST":
            return True

        uuid = str(uuid4())
        if method == "GET" or method == "PATCH":
            uuid = endpoint.split("/")[-1]
            if "-" not in uuid:
                return []

        body_params.update(dict(id=uuid))

        if "triggerWebhook" in endpoint:
            body_params["STATUS"] = "OK"

        return body_params


class MockClient(Client):
    """Mock Client class"""

    def __init__(self, verbosity: str = None, async_execution: bool = False):
        self.playground = False
        self._access_token = None
        self.access_token = None
        self.environment = None
        self.universe_id = None
        self.workspace_id = None
        self.board_id = None
        self.menu_path_id = None

        self.configure_logging = configure_logging
        if verbosity:
            self.configure_logging(verbosity)

        self._api_client = MockApiClient()

        self._universe_object = Universe(self._api_client, uuid="1")
        self._business_object: Optional[Business] = None
        self._app_object: Optional[App] = None
        self._dashboard_object: Optional[Dashboard] = None

        self.epc = AutoAsyncExecutionPool(api_client=self._api_client)

        if async_execution:
            self.activate_async_execution()
        else:
            self.activate_sequential_execution()

        self.universes = UniversesLayer(self._api_client, self.epc)
        self.workspaces = WorkspacessLayer(self._universe_object, self.epc)
        self.boards = BoardsLayer(self._business_object, self.epc)
        self.menu_paths = AppsLayer(self._business_object, self.epc)
        self.components = ReportMetadataApi(self._app_object, self.epc)
        self.data = DataSetManagingApi(self._app_object, self.epc)
        self.io = FileMetadataApi(self._app_object, self.epc)
        self.activities = ActivityMetadataApi(self._app_object, self.epc)
        self.plt = PlotLayer(self._app_object, self.epc)
        self._reuse_data_sets = False
        self._shared_dfs = {}
        self._shared_custom_data = {}

        self.epc.current_app = self._app_object
        self.epc.universe = self._universe_object

        self.html_components = shimoku_components_catalog.html_components
