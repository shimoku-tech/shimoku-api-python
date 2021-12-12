""""""
import json
from typing import List, Dict, Optional, Union

from pandas import DataFrame

from .explorer_api import (
    UniverseExplorerApi, BusinessExplorerApi, ReportExplorerApi, CreateExplorerAPI
)
from .data_managing_api import DataManagingApi


class PlotAux():
    _find_app_type_by_name_filter = (
        CascadeExplorerAPI.find_app_type_by_name_filter
    )
    _get_app_reports = CascadeExplorerAPI.get_app_reports
    _create_app_type = CreateExplorerAPI.create_app_type
    _create_app = CreateExplorerAPI.create_app
    _get_business_apps = BusinessExplorerApi.get_business_apps


class PlotApi(PlotAux):
    """
    """

    def __init__(self, api_client, **kwargs):
        self.api_client = api_client
        
        if kwargs.get('business_id'):
            self.business_id: Optional[str] = kwargs['business_id']
        else:
            self.business_id: Optional[str] = None

    def _create_menu_path(self, menu_path: str) -> Tuple[str, str]:
        """Break the menu path in the app type normalized name
        and the path normalized name if any"""
        app_type_normalized_name: str = menu_path.split('/')[0]
        app_type_name: str = (
            ' '.join(app_type_normalized_name.split('-')).capitalize()
        )

        try:
            path_normalized_name: str = menu_path.split('/')[1]
            path_name: str = (
                ' '.join(path_normalized_name.split('-')).capitalize()
            )
        except IndexError:
            path_normalized_name = None

        return app_type_name, path_name

# TODO this method must go somewhere else
    def _get_app_from_app_type_normalized_name(self, app_type_name: str) -> Dict:
        """Create AppType and App if required and return the App component
        """
        try:
            app_type: Dict = self._create_app_type(name=app_type_name)
        except ValueError:  # It already exists then
            app_type: Dict = (
                self._find_app_type_by_name_filter(name=app_type_name)
            )

        app_type_id: str = app_type['id']
        apps: Dict = self._get_business_apps(business_id=self.business_id)
        target_apps = [app for app in apps if app['appType']['id'] == app_type_id]

        if not apps:
            app: Dict = (
                self._create_app(
                    business_id=self.business_id,
                    app_type_id=app_type_id,
                )
            )
        else:
            app: Dict = target_apps[0]
        return app

    def _create_chart(
        self, data: Union[str, DataFrame, List[Dict]],
        menu_path: str, report_metadata: Dict,
    ) -> Dict:
        """"""
        app_type_name, path_name = self._create_menu_path(menu_path=menu_path)
        app: Dict = self._get_app_from_app_type_normalized_name(app_type_name)

        reports = self._get_app_reports(
            business_id=self.business_id,
            app_id=app['id'],
        )

        if reports:
            order = min([
                report['order']
                for report in reports
                if report['path'] == path_name
            ])
        else:
            orders = max([report['order'] for report in reports])
            order: int = orders + 1

        report_metadata.update({'path': path_name})
        report_metadata.update({'order': order})

        report: Dict = self.create_report(
            business_id=self.business_id,
            app_id=self.app_id,
            report_metadata=report_metadata,
        )
        report_id: str = report['id']

        self.update_report_data(
            business_id=self.business_id,
            app_id=self.app_id,
            report_id=report_id,
            report_data=data,
        )

    def _set_data_fields(
        self, x: str, y: str, x_axis_name: str, y_axis_name: str
    ) -> Dict:
        """"""
        data_fields = {
            "key": x,
            "values": y,
        }

        labels: Dict = {}
        if x_axis_name:
            labels.update({"key": x_axis_name})
        if y_axis_name:
            labels.update({"value": y_axis_name})

        if labels:
            data_fields.update({'labels': labels})

        return data_fields

    def _validate_data(
        self, data: Union[str, DataFrame, List[Dict]], elements: List[str],
    ):
        """"""
        if isinstance(data, DataFrame):
            cols = data.columns
            try:
                assert all([element in cols for element in elements])
                # TODO
            except AssertionError:
                raise ValueError(
                    'Some column names you are specifying '
                    'are not in the input dataframe'
                )
        elif isinstance(data, list):
            try:
                assert all([
                    element in d.keys()
                    for element in elements
                    for d in data
                ])
            except AssertionError:
                raise ValueError(
                    'Some column names you are specifying '
                    'are not in the input list of dictionaries'
                )
        elif isinstance(data, list):
            d: List[Dict] = json.loads(data)
            try:
                assert all([
                    element in d.keys()
                    for element in elements
                    for d in data
                ])
            except AssertionError:
                raise ValueError(
                    'Some column names you are specifying '
                    'are not in the input json'
                )
        else:
            raise ValueError(
                'Input data must be a pandas dataframe, '
                'a json or a list of dictionaries'
            )

    def set_business(
        self, business_id: str, app_id: str,
    ):
        """"""
        self.business_id: str = business_id

    def bar(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
    ):
        """Create a barchart

        Example
        -------------------
        input
            data:
                val_a, val_b,
                  mon,     7,
                  tue,     10,
                  wed,     11,
                  thu,     20,
                  fri,     27,
            x: 'val_a'
            y: 'val_b'
            menu_path: 'purchases/weekly'
            row: 2
            column: 1
            title: 'Purchases by week'
            color: None
            third_layer: {}

        :param data:
        :param x:
        :param y:
        :param menu_path: it contain the `app_name/path` for instance "product-suite/results"
            and it will use the AppType ProductSuite (if it does not it will create it)
            then it will check if the App exists, if not create it and finally create
            the report with the specific path "results"
        :param row:
        :param column:
        :param title:
        :param color:
        :param third_layer:
        """
# TODO pending to be done the validation that x y exists in data
        self._validate_data(data, elements=[x, y])
        data_fields: Dict = self._set_data_fields(x, y, x_axis_name, y_axis_name)

        report_metadata: Dict = {
            'reportType': 'BARCHART',
            'title': title,
            'grid': f'{row}, {column}',
            'dataFields': data_fields,
        }

# TODO pending añadir la third layer

        return self._create_chart(report_metadata)

    def line(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
    ):
        """"""
        raise NotImplementedError

    def predictive_line(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
    ):
        """"""
        raise NotImplementedError

    def stockline(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
    ):
        """"""
        raise NotImplementedError

    def scatter(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
    ):
        """"""
        raise NotImplementedError

    def bubble_chart(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str], z: str, # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
    ):
        """"""
        raise NotImplementedError

    def indicator(
        self, data: Union[str, DataFrame, List[Dict]],
        menu_path: str, row: int, column: int,  # report creation
        header: Optional[str] = None, # second layer
        footer: Optional[str] = None,
        color: Optional[str] = None,
    ):
        """"""
        raise NotImplementedError

    def alert_indicator(
        self, data: Union[str, DataFrame, List[Dict]],
        menu_path: str, row: int, column: int,  # report creation
        header: Optional[str] = None, # second layer
        footer: Optional[str] = None,
        color: Optional[str] = None,
    ):
        """"""
        raise NotImplementedError

    def set_filter():
        raise NotImplementedError
