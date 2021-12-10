""""""
import json
from typing import List, Dict, Optional, Union

from pandas import DataFrame

from .explorer_api import ReportExplorerApi
from .data_managing_api import DataManagingApi


class PlotApi(ReportExplorerApi):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def bar(
        self, business_id: str, app_id: str,
        data: Union[str, DataFrame, List[Dict]],
        x: str, y: str,
        second_layer: Dict,
        third_layer: Dict,
        report_id: Optional[str] = None,
        report_metadata: Optional[Dict] = None,
    ):
        """"""
        if not report_id:
            if not report_metadata:
                raise ValueError('You have to provide either a report_id or its metadata')
            report: Dict = self.create_report(
                business_id=business_id,
                app_id=app_id,
                report_metadata=report_metadata,
            )
            report_id: str = report['id']
        else:
            report: Dict = self.get_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
            )

# TODO seguramente tengo que actualizar los dataFields
#  tambien con x y y y algo de data resistance
        self.update_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
            report_metadata={'reportType': 'BARCHART'}
        )

        self.update_report_data(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
            report_data=data,
        )
