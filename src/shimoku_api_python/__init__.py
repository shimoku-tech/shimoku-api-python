from __future__ import absolute_import

# import apis into sdk package
from shimoku_api_python.api.universe_metadata_api import UniverseMetadataApi
from shimoku_api_python.api.business_metadata_api import BusinessMetadataApi
from shimoku_api_python.api.app_metadata_api import AppMetadataApi
from shimoku_api_python.api.app_type_metadata_api import AppTypeMetadataApi
from shimoku_api_python.api.report_metadata_api import ReportMetadataApi
from shimoku_api_python.api.data_managing_api import DataManagingApi
from shimoku_api_python.api.file_metadata_api import FileMetadataApi
from shimoku_api_python.api.plot_api import PlotApi
from shimoku_api_python.api.ai_api import AiAPI
from shimoku_api_python.api.ping_api import PingApi

from shimoku_api_python.client import ApiClient
# from shimoku_api_python.configuration import Configuration


class Client(object):
    def __init__(self, universe_id: str, environment: str = 'production',
                 access_token: str = "", config={}, business_id: str = ""):

        if access_token and access_token != "":
            config = {'access_token': access_token}

        self._api_client = ApiClient(
            config=config,
            universe_id=universe_id,
            environment=environment,
        )

        self.ping = PingApi(self._api_client)

        self.universe = UniverseMetadataApi(self._api_client)
        self.business = BusinessMetadataApi(self._api_client)
        self.app_type = AppTypeMetadataApi(self._api_client)
        self.app = AppMetadataApi(self._api_client, business_id=business_id)
        self.report = ReportMetadataApi(self._api_client)
        self.data = DataManagingApi(self._api_client)
        self.io = FileMetadataApi(self._api_client, business_id=business_id)
        self.plt = PlotApi(self._api_client, business_id=business_id)
        self.ai = AiAPI(self._api_client)

    def set_config(self, config={}):
        self.api_client.set_config(config)
