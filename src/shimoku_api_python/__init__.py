from __future__ import absolute_import

# import apis into sdk package
from shimoku_api_python.api.business_metadata_api import BusinessMetadataApi
from shimoku_api_python.api.app_metadata_api import AppMetadataApi
from shimoku_api_python.api.path_metadata_api import PathMetadataApi
from shimoku_api_python.api.report_metadata_api import ReportMetadataApi
from shimoku_api_python.api.explorer_api import ExplorerApi
from shimoku_api_python.api.ping_api import PingApi

from shimoku_api_python.client import ApiClient
from shimoku_api_python.configuration import Configuration


class Client(object):
    def __init__(self, config={}, universe_id: str):
        self.api_client = ApiClient(config=config, universe_id=universe_id)

        self.ping = PingApi(self.api_client)
        self.explorer = ExplorerApi(self.api_client)

        self.business = BusinessMetadataApi(self.api_client)
        self.app = AppMetadataApi(self.api_client)
        self.path = PathMetadataApi(self.api_client)
        self.report = ReportMetadataApi(self.api_client)

    def set_config(self, config={}):
        self.api_client.set_config(config)
