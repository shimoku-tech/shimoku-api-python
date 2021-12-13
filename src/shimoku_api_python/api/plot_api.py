""""""
import json
from typing import List, Dict, Optional, Union, Tuple

from pandas import DataFrame

from .data_managing_api import DataValidation
from .explorer_api import (
    UniverseExplorerApi, BusinessExplorerApi, ReportExplorerApi,
    CreateExplorerAPI, CascadeExplorerAPI, MultiCreateApi
)


class PlotAux():
    _find_app_type_by_name_filter = (
        CascadeExplorerAPI.find_app_type_by_name_filter
    )
    get_universe_app_types = CascadeExplorerAPI.get_universe_app_types

    _get_app_reports = CascadeExplorerAPI.get_app_reports
    _create_app_type = CreateExplorerAPI.create_app_type
    _create_app = CreateExplorerAPI.create_app
    _get_business_apps = BusinessExplorerApi.get_business_apps

    _validate_data = DataValidation._validate_data
    _validate_data_is_pandarable = DataValidation._validate_data_is_pandarable

    _create_app_type_and_app = MultiCreateApi.create_app_type_and_app


class PlotApi(PlotAux):
    """
    """

    def __init__(self, api_client, **kwargs):
        self.api_client = api_client
        
        if kwargs.get('business_id'):
            self.business_id: Optional[str] = kwargs['business_id']
        else:
            self.business_id: Optional[str] = None

    def set_business(self, business_id: str):
        """"""
        self.business_id: str = business_id

    def _clean_menu_path(self, menu_path: str) -> Tuple[str, str]:
        """Break the menu path in the app type normalized name
        and the path normalized name if any"""
        # remove empty spaces and put everything in lower case
        menu_path: str = menu_path.strip().lower()
        # Split AppType Normalized Name
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

    def _create_chart(
        self, data: Union[str, DataFrame, List[Dict]],
        menu_path: str, report_metadata: Dict,
        third_layer: Optional[Dict] = None,
    ) -> Dict:
        """"""
        if third_layer:
            report_metadata.update(third_layer)

        app_type_name, path_name = self._clean_menu_path(menu_path=menu_path)
        d: Dict[str, Dict] = self._create_app_type_and_app(
            business_id=self.business_id,
            app_type_metadata={'name': app_type_name},
            app_metadata={},
        )
        app: Dict = d['app']

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
            apps: List[Dict] = self._get_business_apps(self.business_id)

            orders: int = 0
            for app in apps:
                reports_ = self._get_app_reports(
                    business_id=self.business_id,
                    app_id=app['id'],
                )
                order_temp = max([report['order'] for report in reports])
                orders = max(orders, order_temp)
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

    def _create_trend_chart(
        self, report_type: str,
        data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
        filters=filters,
    ):
        """For Linechart, Barchart, Stocklinechart, Scatter chart, and alike

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
        :param filters: To create a filter for every specified column
        """
        self._validate_data(data, elements=[x] + y)
        data_fields: Dict = self._set_data_fields(x, y, x_axis_name, y_axis_name)

        report_metadata: Dict = {
            'reportType': report_type,
            'title': title,
            'grid': f'{row}, {column}',
            'dataFields': data_fields,
        }

        if filters:
            raise NotImplementedError

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
            third_layer=third_layer,
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

    def bar(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """Create a barchart
        """
        self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, color=color,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            third_layer=third_layer,
            report_type='BARCHART',
            filters=filters,
        )

    def line(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """"""
        self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, color=color,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            third_layer=third_layer,
            report_type='LINECHART',
            filters=filters,
        )

    def predictive_line(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """"""
        raise NotImplementedError

    def line_with_confidence_area(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
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
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """"""
        self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, color=color,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            third_layer=third_layer,
            report_type='STOCKLINECHART',
            filters=filters,
        )

    def scatter(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        color: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        third_layer: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """"""
        self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, color=color,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            third_layer=third_layer,
            report_type='SCATTER',
            filters=filters,
        )

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
        self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, color=color,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            third_layer=third_layer,
            report_type='SCATTER',
            filters=filters,
        )

    def indicator(
        self, data: Union[str, DataFrame, List[Dict]],
        menu_path: str, row: int, column: int,  # report creation
        header: Optional[str] = None, # second layer
        footer: Optional[str] = None,
        color: Optional[str] = None,
    ):
        """"""
        elements: List[str] = [
            'title', 'description', 'value',
        ]
        self._validate_data(data, elements=elements)

        report_metadata: Dict = {
            'reportType': 'INDICATOR',
            'title': title,
            'grid': f'{row}, {column}',
            'dataFields': data_fields,
        }

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
        )

    def alert_indicator(
        self, data: Union[str, DataFrame, List[Dict]],
        menu_path: str, row: int, column: int,  # report creation
        link_url: str,  # Where it sends you if click
        header: Optional[str] = None, # second layer
        footer: Optional[str] = None,
        color: Optional[str] = None,
    ):
        """"""
        elements: List[str] = [
            'title', 'description', 'value', 'link'  # TODO validate this one
        ]
        self._validate_data(data, elements=elements)

        report_metadata: Dict = {
            'reportType': 'INDICATOR',
            'title': title,
            'grid': f'{row}, {column}',
            'dataFields': data_fields,
        }

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
        )

    def pie(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str,  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        third_layer: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """Create a Piechart
        """
        self._validate_data(data, elements=[x, y])

        report_metadata: Dict = {
            'reportType': 'PIECHART',
            'title': title,
            'grid': f'{row}, {column}',
        }

        if filters:
            raise NotImplementedError

# TODO quedarme solo con la data de las columnas x, y!!!!!
#  HACER LO MISMO PARA EL RESTO DE CHARTS
        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
            third_layer=third_layer,
        )

    def radar(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        third_layer: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """Create a RADAR
        """
        self._validate_data(data, elements=[x] + y)

        report_metadata: Dict = {
            'reportType': 'RADAR',
            'title': title,
            'grid': f'{row}, {column}',
        }

        if filters:
            raise NotImplementedError

        # TODO quedarme solo con la data de las columnas x, y!!!!!
        #  HACER LO MISMO PARA EL RESTO DE CHARTS
        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
            third_layer=third_layer,
        )

    def Tree(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[Dict],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        third_layer: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """Create a Tree
        """
        # TODO validate tree data

        report_metadata: Dict = {
            'reportType': 'TREE',
            'title': title,
            'grid': f'{row}, {column}',
        }

        if filters:
            raise NotImplementedError

        # TODO quedarme solo con la data de las columnas x, y!!!!!
        #  HACER LO MISMO PARA EL RESTO DE CHARTS
        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
            third_layer=third_layer,
        )

    def Treemap(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[Dict],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        third_layer: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """Create a Tree
        """
        # TODO validate treemap data

        report_metadata: Dict = {
            'reportType': 'TREE',
            'title': title,
            'grid': f'{row}, {column}',
        }

        if filters:
            raise NotImplementedError

        # TODO quedarme solo con la data de las columnas x, y!!!!!
        #  HACER LO MISMO PARA EL RESTO DE CHARTS
        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
            third_layer=third_layer,
        )

    def Sunburst(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[Dict],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        third_layer: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """Create a Tree
        """
        # TODO validate treemap data

        report_metadata: Dict = {
            'reportType': 'TREE',
            'title': title,
            'grid': f'{row}, {column}',
        }

        if filters:
            raise NotImplementedError

        # TODO quedarme solo con la data de las columnas x, y!!!!!
        #  HACER LO MISMO PARA EL RESTO DE CHARTS
        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
            third_layer=third_layer,
        )
