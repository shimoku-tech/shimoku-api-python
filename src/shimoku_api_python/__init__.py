from __future__ import absolute_import

# import apis into sdk package
from shimoku_api_python.api.universe_metadata_api import UniverseMetadataApi
from shimoku_api_python.api.business_metadata_api import BusinessMetadataApi
from shimoku_api_python.api.app_metadata_api import AppMetadataApi
from shimoku_api_python.api.app_type_metadata_api import AppTypeMetadataApi
from shimoku_api_python.api.path_metadata_api import PathMetadataApi
from shimoku_api_python.api.report_metadata_api import ReportMetadataApi
from shimoku_api_python.api.data_managing_api import DataManagingApi
from shimoku_api_python.api.plot_api import PlotApi
from shimoku_api_python.api.suite_api import SuiteApi
from shimoku_api_python.api.ping_api import PingApi

from shimoku_api_python.client import ApiClient
# from shimoku_api_python.configuration import Configuration


class Client(object):
    def __init__(self, universe_id: str, environment: str = 'staging', config={}):
        self._api_client = ApiClient(
            config=config,
            universe_id=universe_id,
            environment=environment,
        )

        self.ping = PingApi(self._api_client)

        self.universe = UniverseMetadataApi(self._api_client)
        self.business = BusinessMetadataApi(self._api_client)
        self.app_type = AppTypeMetadataApi(self._api_client)
        self.app = AppMetadataApi(self._api_client)
        self.path = PathMetadataApi(self._api_client)
        self.report = ReportMetadataApi(self._api_client)
        self.data = DataManagingApi(self._api_client)
        self.plt = PlotApi(self._api_client)

        self.suite = SuiteApi(self)  # it takes all the others classes

    def set_config(self, config={}):
        self.api_client.set_config(config)
