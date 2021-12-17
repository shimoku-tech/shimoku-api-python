""""""
from typing import List, Dict, Optional, Union, Tuple, Any
import json

from pandas import DataFrame

from .data_managing_api import DataValidation
from .explorer_api import (
    BusinessExplorerApi, CreateExplorerAPI, CascadeExplorerAPI,
    MultiCreateApi, ReportExplorerApi,
)
from .data_managing_api import DataManagingApi
from .app_type_metadata_api import AppTypeMetadataApi
from .app_metadata_api import AppMetadataApi


class PlotAux:
    _get_business_apps = BusinessExplorerApi.get_business_apps

    get_report = ReportExplorerApi.get_report
    _get_report_with_data = ReportExplorerApi._get_report_with_data
    _update_report = ReportExplorerApi.update_report

    _find_app_type_by_name_filter = (
        CascadeExplorerAPI.find_app_type_by_name_filter
    )
    # TODO this shit has to be fixed
    get_universe_app_types = CascadeExplorerAPI.get_universe_app_types
    _get_universe_app_types = CascadeExplorerAPI.get_universe_app_types
    _get_app_reports = CascadeExplorerAPI.get_app_reports

    _create_report = CreateExplorerAPI.create_report
    _create_app_type = CreateExplorerAPI.create_app_type
    _create_app = CreateExplorerAPI.create_app

    _get_app_type_by_name = AppTypeMetadataApi.get_app_type_by_name
    _get_app_by_type = AppMetadataApi.get_app_by_type

    _update_report_data = DataManagingApi.update_report_data
    _transform_report_data_to_chart_data = DataManagingApi._transform_report_data_to_chart_data
    _is_report_data_empty = DataManagingApi._is_report_data_empty

    _validate_table_data = DataValidation._validate_table_data
    _validate_tree_data = DataValidation._validate_tree_data
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

        try:
            assert len(menu_path.split('/')) <= 2  # we allow only one level of path
        except AssertionError:
            raise ValueError(
                f'We only allow one subpath in your request | '
                f'you introduced {menu_path} it should be maximum '
                f'{"/".join(menu_path.split("/")[:1])}'
            )

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
    ) -> Dict:
        """"""
        app_type_name, path_name = self._clean_menu_path(menu_path=menu_path)
        d: Dict[str, Dict] = self._create_app_type_and_app(
            business_id=self.business_id,
            app_type_metadata={'name': app_type_name},
            app_metadata={},
        )
        app: Dict = d['app']
        app_id: str = app['id']

        reports = self._get_app_reports(
            business_id=self.business_id,
            app_id=app_id,
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
            for app_ in apps:
                reports_ = self._get_app_reports(
                    business_id=self.business_id,
                    app_id=app_['id'],
                )

                try:
                    order_temp = max([report['order'] for report in reports])
                except ValueError:
                    order_temp = 0

                orders = max(orders, order_temp)
            order: int = orders + 1

        report_metadata.update({'path': path_name})
        report_metadata.update({'order': order})

        if report_metadata.get('dataFields'):
            report_metadata['dataFields'] = json.dumps(report_metadata['dataFields'])

        report: Dict = self._create_report(
            business_id=self.business_id,
            app_id=app_id,
            report_metadata=report_metadata,
        )
        report_id: str = report['id']

        self._update_report_data(
            business_id=self.business_id,
            app_id=app_id,
            report_id=report_id,
            report_data=data,
        )

    # TODO move part of it to get_reports_by_path_grid_and_type() in report_metadata_api.py
    def delete(
        self, menu_path: str,
        type: str, row: int, column: int,
    ) -> None:
        """In cascade find the reports that match the query
        and delete them all
        """
        grid: str = f'{row} {column}'
        app_type_name, path_name = self._clean_menu_path(menu_path=menu_path)
        app_type: Dict = self._get_app_type_by_name(name=app_type_name)

        app: Dict = self._get_app_by_type(
            business_id=self.business_id,
            app_type_id=app_type['id']
        )
        app_id: str = app['id']

        reports: List[Dict] = self._get_app_reports(
            business_id=self.business_id, app_id=app_id,
        )

        target_reports: List[Dict] = [
            report
            for report in reports
            if (
                    report['path'] == path_name
                    and report['grid'] == grid
                    and report['reportType'] == type
            )
        ]

        for report in target_reports:
            self._delete_report(
                business_id=self.business_id,
                app_id=app_id,
                report_id=report['id']
            )

    def _create_trend_chart(
        self, echart_type: str,
        data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
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
            option_modifications: {}

        :param echart_type:
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
        :param option_modifications:
        :param filters: To create a filter for every specified column
        """
        self._validate_table_data(data, elements=[x] + y)
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[x] + y]  # keep only x and y
        df.rename(columns={x: 'xAxis'}, inplace=True)

        # TODO we have two titles now, take a decision
        #  one in dataFields the other as field
        data_fields: Dict = self._set_data_fields(
            x=x, y=y,
            title='', subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
        )
        data_fields['type'] = echart_type

        report_metadata: Dict = {
            'reportType': 'ECHARTS',
            'dataFields': data_fields,
            'title': title,
            'grid': f'{row}, {column}',
        }

        if filters:
            raise NotImplementedError

        return self._create_chart(
            data=df,
            menu_path=menu_path,
            report_metadata=report_metadata,
        )

    def _set_data_fields(
        self, x: str, y: str,
        title: str, subtitle: str,
        x_axis_name: str, y_axis_name: str,
        option_modifications: Dict,
    ) -> Dict:
        """"""
        chart_options: Dict = {
            'title': title if title else "",
            'subtitle': subtitle if subtitle else "",
            'legend': True,
            'tooltip': True,
            'axisPointer': True,
            'toolbox': {
                'saveAsImage': True,
                'restore': True,
                'dataView': False,
                'dataZoom': True,
                'magicType': False,
            },
            'xAxis': {
                'name': x_axis_name if x_axis_name else "",
                'type': 'category',
            },
            'yAxis': {
                'name': y_axis_name if y_axis_name else "",
                'type': 'value',
            },
            'dataZoom': True,
            'smooth': True,
        }

        data_fields: Dict = {
            'chart_options': chart_options,
        }

        if option_modifications:
            data_fields['optionModifications'] = option_modifications

        return data_fields

    # TODO
    def table(self):
        raise NotImplementedError

    def bar(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """Create a barchart
        """
        return self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='bar',
            filters=filters,
        )

    def line(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # thid layer
        filters: Optional[List[str]] = None,  # thid layer
    ):
        """"""
        return self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='line',
            filters=filters,
        )

    def predictive_line(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        min_value_mark: Any, max_value_mark: Any,
        color_mark: str = 'rgba(255, 173, 177, 0.4)',
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        filters: Optional[List[str]] = None,
    ):
        """
        :param data:
        :param x:
        :param y:
        :param menu_path:
        :param row:
        :param column:
        :param min_value_mark:
        :param max_value_mark:
        :param color_mark: RGBA code
        :param title:
        :param x_axis_name:
        :param y_axis_name:
        :param filters:
        """
        option_modifications = {
            'series': [{
                'smooth': True,
                'markArea': {
                    'itemStyle': {
                        'color': color_mark
                    },
                    'data': [
                        [
                            {
                                'name': 'Prediction',
                                'xAxis': min_value_mark
                            },
                            {
                                'xAxis': max_value_mark
                            }
                        ],
                    ],
                }
            },],
        }

        return self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='line',
            filters=filters,
        )

    def line_with_confidence_area(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str,  #  above_band_name: str, below_band_name: str,
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        filters: Optional[List[str]] = None,
    ):
        """
        https://echarts.apache.org/examples/en/editor.html?c=line-stack

        option = {
          title: {
            text: 'Stacked Line'
          },
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: ['Email', 'Union Ads', 'Video Ads', 'Direct', 'Search Engine']
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          toolbox: {
            feature: {
              saveAsImage: {}
            }
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: 'Email',
              type: 'line',
              stack: 'Total',
              data: [120, 132, 101, 134, 90, 230, 210]
            },
            {
              name: 'Union Ads',
              type: 'line',
              stack: 'Total',
              lineStyle: {
                opacity: 0
              },
              stack: 'confidence-band',
              symbol: 'none',
              data: [220, 182, 191, 234, 290, 330, 310]
            },
            {
              name: 'Video Ads',
              type: 'line',
              stack: 'Total',
              data: [150, 232, 201, 154, 190, 330, 410]
            },
            {
              name: 'Direct',
              type: 'line',
              data: [320, 332, 301, 334, 390, 330, 320]
            },
            {
              name: 'Search Engine',
              type: 'line',
              lineStyle: {
                opacity: 0
              },
              areaStyle: {
                color: '#ccc'
              },
              stack: 'confidence-band',
              symbol: 'none',
              data: [820, 932, 901, 934, 1290, 1330, 1320]
            }
          ]
        };

        """
        option_modifications = {
            'series': [{
                'smooth': True,
                'lineStyle': {
                    'opacity': 0
                },
                'areaStyle': {
                    'color': '#ccc'
                },
                'stack': 'confidence-band',
                'symbol': 'none',
            }, ],
        }

        return self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='line',
            filters=filters,
        )

    def scatter_with_confidence_area(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str,  #  above_band_name: str, below_band_name: str,
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        filters: Optional[List[str]] = None,
    ):
        """
        https://echarts.apache.org/examples/en/editor.html?c=line-stack

        option = {
          title: {
            text: 'Stacked Line'
          },
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: ['Email', 'Union Ads', 'Video Ads', 'Direct', 'Search Engine']
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          toolbox: {
            feature: {
              saveAsImage: {}
            }
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: 'Email',
              type: 'line',
              stack: 'Total',
              data: [120, 132, 101, 134, 90, 230, 210]
            },
            {
              name: 'Union Ads',
              type: 'line',
              stack: 'Total',
              lineStyle: {
                opacity: 0
              },
              stack: 'confidence-band',
              symbol: 'none',
              data: [220, 182, 191, 234, 290, 330, 310]
            },
            {
              name: 'Video Ads',
              type: 'line',
              stack: 'Total',
              data: [150, 232, 201, 154, 190, 330, 410]
            },
            {
              name: 'Direct',
              type: 'line',
              data: [320, 332, 301, 334, 390, 330, 320]
            },
            {
              name: 'Search Engine',
              type: 'line',
              lineStyle: {
                opacity: 0
              },
              areaStyle: {
                color: '#ccc'
              },
              stack: 'confidence-band',
              symbol: 'none',
              data: [820, 932, 901, 934, 1290, 1330, 1320]
            }
          ]
        };

        """
        option_modifications = {
            'series': [{
                'smooth': True,
                'lineStyle': {
                    'opacity': 0
                },
                'areaStyle': {
                    'color': '#ccc'
                },
                'stack': 'confidence-band',
                'symbol': 'none',
            }, ],
        }

        return self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='scatter',
            filters=filters,
        )

    # TODO this is not a ECHART
    def stockline(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """"""
        return self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='STOCKLINECHART',
            filters=filters,
        )

    def scatter(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """"""
        try:
            assert 2 <= len(y) <= 3
        except Exception:
            raise ValueError(f'y provided has {len(y)} it has to have 2 or 3 dimensions')

        return self._create_trend_chart(
            data=df, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='scatter',
            filters=filters,
        )

    def bubble_chart(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str], z: str, # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,  # to create filters
    ):
        """"""
        return self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='scatter',
            filters=filters,
        )

    def indicator(
        self, data: Union[str, DataFrame, List[Dict]], value: str,
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,
        header: Optional[str] = None,
        footer: Optional[str] = None,
        color: Optional[str] = None,
    ):
        """"""
        elements: List[str] = [header, footer, value, color]
        self._validate_table_data(data, elements=elements)
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[elements]  # keep only x and y
        cols_to_rename: Dict[str, str] = {
            header: 'title',
            footer: 'description',
            value: 'value',
        }
        df.rename(columns={cols_to_rename}, inplace=True)

        report_metadata: Dict = {
            'reportType': 'INDICATOR',
            'grid': f'{row}, {column}',
        }

        if title:
            report_metadata['title'] = title

        return self._create_chart(
            data=df,
            menu_path=menu_path,
            report_metadata=report_metadata,
        )

    def alert_indicator(
        self, data: Union[str, DataFrame, List[Dict]],
        value: str, link_url: str,
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,
        header: Optional[str] = None,
        footer: Optional[str] = None,
        color: Optional[str] = None,
    ):
        """"""
        elements: List[str] = [header, footer, value, color, link_url]
        self._validate_table_data(data, elements=elements)
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[elements]  # keep only x and y
        cols_to_rename: Dict[str, str] = {
            header: 'title',
            footer: 'description',
            value: 'value',
        }
        df.rename(columns={cols_to_rename}, inplace=True)

        report_metadata: Dict = {
            'reportType': 'INDICATOR',
            'grid': f'{row}, {column}',
        }

        if title:
            report_metadata['title'] = title

        return self._create_chart(
            data=df,
            menu_path=menu_path,
            report_metadata=report_metadata,
        )

    def pie(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str,  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """Create a Piechart
        """
        self._validate_table_data(data, elements=[x, y])
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[x, y]]  # keep only x and y
        df.rename(columns={x: 'name', y: 'value'}, inplace=True)

        report_metadata: Dict = {
            'reportType': 'ECHARTS',
            'dataFields': {'type': 'pie'},
            'title': title,
            'grid': f'{row}, {column}',
        }

        if filters:
            raise NotImplementedError

        return self._create_chart(
            data=df,
            menu_path=menu_path,
            report_metadata=report_metadata,
            option_modifications=option_modifications,
        )

    def radar(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: List[str],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """Create a RADAR
        """
        self._validate_table_data(data, elements=[x] + y)
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[x] + y]  # keep only x and y
        df.rename(columns={x: 'name'}, inplace=True)

        report_metadata: Dict = {
            'reportType': 'ECHARTS',
            'dataFields': {'type': 'radar'},
            'title': title,
            'grid': f'{row}, {column}',
        }

        if filters:
            raise NotImplementedError

        return self._create_chart(
            data=df,
            menu_path=menu_path,
            report_metadata=report_metadata,
            option_modifications=option_modifications,
        )

    def tree(
        self, data: Union[str, List[Dict]],
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """Create a Tree
        """
        self._validate_tree_data(data, vals=['name', 'value', 'children'])

        report_metadata: Dict = {
            'reportType': 'ECHARTS',
            'dataFields': {'type': 'tree'},
            'title': title,
            'grid': f'{row}, {column}',
        }

        if filters:
            raise NotImplementedError

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
            option_modifications=option_modifications,
        )

    def treemap(
        self, data: Union[str, List[Dict]],
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """Create a Treemap
        """
        self._validate_tree_data(data, vals=['name', 'value', 'children'])

        report_metadata: Dict = {
            'title': title,
            'grid': f'{row}, {column}',
            'reportType': 'ECHARTS',
            'dataFields': {'type': 'treemap'},
        }

        if filters:
            raise NotImplementedError

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
            option_modifications=option_modifications,
        )

    def sunburst(
        self, data: Union[str, DataFrame, List[Dict]],
        name: str, children: List[Dict],  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """Create a Tree
        """
        self._validate_tree_data(data, vals=['name', 'children'])
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[name, children]]  # keep only x and y
        df.rename(
            columns={
                name: 'name',
                children: 'children',
            },
            inplace=True,
        )

        report_metadata: Dict = {
            'reportType': 'ECHARTS',
            'title': title,
            'grid': f'{row}, {column}',
            'dataFields': {'type': 'sunburst'},
        }

        if filters:
            raise NotImplementedError

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            report_metadata=report_metadata,
            option_modifications=option_modifications,
        )

    def candlestick(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str,
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """"""
        y = ['open', 'close', 'highest', 'lowest']
        return self._create_trend_chart(
            data=data, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle, color=color,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='CANDLESTICK',
            filters=filters,
        )

    def heatmap(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str, value: str,
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """"""
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[x, y, value]]  # keep only x and y
        df.rename(columns={x: 'xAxis', y: 'yAxis', value: 'value'}, inplace=True)
        return self._create_trend_chart(
            data=df, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='HEATMAP',
            filters=filters,
        )

    def cohort(self):
        """"""
        raise NotImplementedError

    def predictive_cohort(self):
        """"""
        raise NotImplementedError

    def sankey(
        self, data: Union[str, DataFrame, List[Dict]],
        source: str, target: str, value: str,
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """"""
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[soruce, target, value]]  # keep only x and y
        df.rename(
            columns={
                source: 'source',
                target: 'target',
                value: 'value',
            },
            inplace=True,
        )

        return self._create_trend_chart(
            data=df, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='SANKEY',
            filters=filters,
        )

    def funnel(
        self, data: Union[str, DataFrame, List[Dict]],
        name: str, value: str,
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """"""
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[name, value]]  # keep only x and y
        df.rename(
            columns={
                name: 'value',
                value: 'value',
            },
            inplace=True,
        )

        return self._create_trend_chart(
            data=df, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='FUNNEL',
            filters=filters,
        )

    def gauge(
        self, data: Union[str, DataFrame, List[Dict]],
        name: str, value: str,
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None,  # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """"""
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[name, value]]  # keep only x and y
        df.rename(
            columns={
                name: 'value',
                value: 'value',
            },
            inplace=True,
        )

        return self._create_trend_chart(
            data=df, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='FUNNEL',
            filters=filters,
        )

    def themeriver(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str, name: str,  # first layer
        menu_path: str, row: int, column: int,  # report creation
        title: Optional[str] = None, # second layer
        subtitle: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        option_modifications: Optional[Dict] = None,  # third layer
        filters: Optional[List[str]] = None,
    ):
        """Create a barchart
        """
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[x, y, name]]  # keep only x and y
        df.rename(
            columns={
                name: 'name',
                y: 'value',
            },
            inplace=True,
        )
        y = [y, name]
        self._create_trend_chart(
            data=df, x=x, y=y, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='THEMERIVER',
            filters=filters,
        )
