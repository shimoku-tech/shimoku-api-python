""""""
from sys import stdout
from typing import List, Dict, Optional, Union, Tuple, Any
import logging
import json

from pandas import DataFrame
import datetime as dt

from .data_managing_api import DataValidation
from .explorer_api import (
    BusinessExplorerApi, CreateExplorerAPI, CascadeExplorerAPI,
    MultiCreateApi, ReportExplorerApi, DeleteExplorerApi, UniverseExplorerApi
)
from .data_managing_api import DataManagingApi
from .app_type_metadata_api import AppTypeMetadataApi

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    stream=stdout,
    datefmt='%Y-%m-%d %H:%M',
    format='%(asctime)s | %(levelname)s | %(message)s'
)


class PlotAux:
    _get_business = BusinessExplorerApi.get_business
    _get_business_apps = BusinessExplorerApi.get_business_apps
    get_business_apps = BusinessExplorerApi.get_business_apps

    get_universe_businesses = UniverseExplorerApi.get_universe_businesses

    get_report = ReportExplorerApi.get_report
    _get_report_with_data = ReportExplorerApi._get_report_with_data
    _update_report = ReportExplorerApi.update_report
    update_report = ReportExplorerApi.update_report
    get_report_data = ReportExplorerApi.get_report_data

    _find_app_type_by_name_filter = (
        CascadeExplorerAPI.find_app_type_by_name_filter
    )
    # TODO this shit has to be fixed
    get_universe_app_types = CascadeExplorerAPI.get_universe_app_types
    _get_universe_app_types = CascadeExplorerAPI.get_universe_app_types
    _get_app_reports = CascadeExplorerAPI.get_app_reports
    _get_app_by_type = CascadeExplorerAPI.get_app_by_type
    _find_business_by_name_filter = CascadeExplorerAPI.find_business_by_name_filter

    _create_report = CreateExplorerAPI.create_report
    _create_app_type = CreateExplorerAPI.create_app_type
    _create_app = CreateExplorerAPI.create_app
    _create_business = CreateExplorerAPI.create_business

    _get_app_type_by_name = AppTypeMetadataApi.get_app_type_by_name

    _update_report_data = DataManagingApi.update_report_data
    _append_report_data = DataManagingApi.append_report_data
    _transform_report_data_to_chart_data = DataManagingApi._transform_report_data_to_chart_data
    _is_report_data_empty = DataManagingApi._is_report_data_empty
    _convert_dataframe_to_report_entry = DataManagingApi._convert_dataframe_to_report_entry
    _set_report_entry_filter_fields = DataManagingApi._set_report_entry_filter_fields
    _create_report_entries = DataManagingApi._create_report_entries

    _validate_table_data = DataValidation._validate_table_data
    _validate_tree_data = DataValidation._validate_tree_data
    _validate_data_is_pandarable = DataValidation._validate_data_is_pandarable

    _create_app_type_and_app = MultiCreateApi.create_app_type_and_app

    _delete_report = DeleteExplorerApi.delete_report
    _delete_app = DeleteExplorerApi.delete_app
    _delete_report_entries = DeleteExplorerApi.delete_report_entries


class PlotApi(PlotAux):
    """
    """

    def __init__(self, api_client, **kwargs):
        self.api_client = api_client

        if kwargs.get('business_id'):
            self.business_id: Optional[str] = kwargs['business_id']
        else:
            self.business_id: Optional[str] = None

    def _find_target_reports(
            self, menu_path: str, row: int, column: int,
            component_type: Optional[str] = None,
            by_component_type: bool = True,
    ) -> List[Dict]:
        type_map = {
            'alert_indicator': 'INDICATORS',
            'indicator': 'INDICATORS',
            'table': None,
            'stockline': 'STOCKLINECHART',
            'html': 'HTML'
        }
        if component_type in type_map.keys():
            component_type = type_map[component_type]
        else:
            component_type = 'ECHARTS'

        grid: str = f'{row}, {column}'
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

        # Delete specific components in a path / grid
        # or all of them whatsoever is its component_type
        if by_component_type:
            target_reports: List[Dict] = [
                report
                for report in reports
                if (
                        report['path'] == path_name
                        and report['grid'] == grid
                        and report['reportType'] == component_type
                )
            ]
        else:  # Whatever is the reportType delete it
            target_reports: List[Dict] = [
                report
                for report in reports
                if (
                        report['path'] == path_name
                        and report['grid'] == grid
                )
            ]

        return target_reports

    def set_business(self, business_id: str):
        """"""
        # If the business id does not exists it raises an ApiClientError
        _ = self._get_business(business_id)
        self.business_id: str = business_id

    def set_new_business(self, name: str):
        """"""
        business: Dict = self._create_business(name=name)
        self.business_id: str = business['id']

    # TODO to be tried
    def set_path_orders(
            self, app_name: str, path_order: Dict[str, int],
    ) -> None:
        """
        :param app_name: the App name
        :param path_order: example {'test': 0, 'more-test': 1}
        """
        apps: List[Dict] = self._get_business_apps(self.business_id)
        app_types: List[Dict] = self.get_universe_app_types()
        for app in apps:
            app_id: str = app['id']
            app_type_id: str = app['type']['id']

            # Check that it is of the target app_name
            if not any([
                True
                if app_type['id'] == app_type_id and app_type['name'] == app_name
                else False
                for app_type in app_types
            ]):
                continue

            reports = self._get_app_reports(
                business_id=self.business_id,
                app_id=app_id,
            )

            for report in reports:
                path: str = report['path']
                order: int = path_order.get(path)
                if order:
                    self.update_report(
                        business_id=self.business_id,
                        app_id=app_id,
                        report_id=report['id'],
                        report_metadata={'order': order},
                    )

    def _get_component_order(self, app_id: str, path_name: str) -> int:
        """Set an ascending report.Order to new path created

        If a report in the same path exists take its order
        otherwise find the higher report.Order and set it +1
        as the report.Order of the new path
        """
        reports_ = self._get_app_reports(
            business_id=self.business_id,
            app_id=app_id,
        )

        try:
            order_temp = max([report['order'] for report in reports_])
        except ValueError:
            order_temp = 0

        path_order: List[int] = [
            report['order']
            for report in reports_
            if report['path'] == path_name
        ]

        if path_order:
            return min(path_order)
        else:
            return order_temp + 1

    def _clean_menu_path(self, menu_path: str) -> Tuple[str, str]:
        """Break the menu path in the app type normalized name
        and the path normalized name if any"""
        # remove empty spaces
        menu_path: str = menu_path.strip()
        # replace "_" for www protocol it is not good
        menu_path = menu_path.replace('_', '-')

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
            ' '.join(app_type_normalized_name.split('-'))
        )

        try:
            path_normalized_name: str = menu_path.split('/')[1]
            path_name: str = (
                ' '.join(path_normalized_name.split('-'))
            )
        except IndexError:
            path_name = None

        return app_type_name, path_name

    def _create_chart(
            self, data: Union[str, DataFrame, List[Dict]],
            menu_path: str, report_metadata: Dict,
            row: Optional[int] = None,
            column: Optional[int] = None,
            overwrite: bool = True,
    ) -> Dict:
        """
        :param data:
        :param menu_path:
        :param report_metadata:
        :param row: Only required for Overwrite
        :param column: Only required for Overwrite
        :param report_type: Only required for Overwrite
        :param overwrite: Whether to Update (delete) any report in
            the same menu_path and grid position or not
        """
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

        order: int = self._get_component_order(
            app_id=app_id, path_name=path_name,
        )

        report_metadata.update({'path': path_name})
        report_metadata.update({'order': order})

        if report_metadata.get('dataFields'):
            report_metadata['dataFields'] = (
                json.dumps(report_metadata['dataFields'])
            )

        if overwrite:
            if not row or not column:
                raise ValueError(
                    'Row and Column must be specified to overwrite a report'
                )

            self.delete(
                menu_path=menu_path,
                row=row, column=column,
                by_component_type=False,
            )

        report: Dict = self._create_report(
            business_id=self.business_id,
            app_id=app_id,
            report_metadata=report_metadata,
        )
        report_id: str = report['id']

        try:
            if data:
                self._update_report_data(
                    business_id=self.business_id,
                    app_id=app_id,
                    report_id=report_id,
                    report_data=data,
                )
        except ValueError:
            if not data.empty:
                self._update_report_data(
                    business_id=self.business_id,
                    app_id=app_id,
                    report_id=report_id,
                    report_data=data,
                )

    def append_data_to_trend_chart(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],
            menu_path: str, row: int, column: int, component_type: str,
    ) -> None:
        """Append new data"""
        allowed_components_type: List[str] = [
            'line', 'bar', 'scatter', 'predictive_line',
        ]

        if component_type not in allowed_components_type:
            raise ValueError(
                f'{component_type} not allowed | '
                f'Must be one of {allowed_components_type}'
            )

        cols: List[str] = [x] + y
        self._validate_table_data(data, elements=cols)
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[cols]  # keep only x and y

        df.rename(columns={x: 'xAxis'}, inplace=True)

        target_reports: List[Dict] = (
            self._find_target_reports(
                menu_path=menu_path, row=row, column=column,
                component_type=component_type,
            )
        )

        # TODO for multifilter we will need to iterate on this
        assert len(target_reports) == 1

        for report in target_reports:
            self._append_report_data(
                business_id=self.business_id,
                app_id=report['appId'],
                report_id=report['id'],
                report_data=df,
            )

    # TODO move part of it to get_reports_by_path_grid_and_type() in report_metadata_api.py
    def delete(
            self, menu_path: str, row: int, column: int,
            component_type: Optional[str] = None,
            by_component_type: bool = True,
    ) -> None:
        """In cascade find the reports that match the query
        and delete them all
        """
        target_reports: List[Dict] = (
            self._find_target_reports(
                menu_path=menu_path, row=row, column=column,
                component_type=component_type,
                by_component_type=by_component_type
            )
        )

        for report in target_reports:
            self._delete_report(
                business_id=self.business_id,
                app_id=report['appId'],
                report_id=report['id']
            )

    def delete_path(self, menu_path: str) -> None:
        """In cascade delete an App or Path and all the reports within it

        If menu_path contains an "{App}/{Path}" then it removes the path
        otherwise it removes the whole app
        """
        app_type_name, path_name = self._clean_menu_path(menu_path=menu_path)
        app_type: Dict = self._get_app_type_by_name(name=app_type_name)

        app: Dict = self._get_app_by_type(
            business_id=self.business_id,
            app_type_id=app_type['id']
        )
        if not app:
            return

        app_id: str = app['id']

        reports: List[Dict] = self._get_app_reports(
            business_id=self.business_id, app_id=app_id,
        )

        if path_name:
            target_reports: List[Dict] = [
                report
                for report in reports
                if report['path'] == path_name
            ]
        else:
            target_reports: List[Dict] = reports

        for report in target_reports:
            self._delete_report(
                business_id=self.business_id,
                app_id=app_id,
                report_id=report['id']
            )
        else:
            if '/' not in menu_path:
                self._delete_app(
                    business_id=self.business_id,
                    app_id=app_id,
                )

    def update(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],  # first layer
            menu_path: str, row: int, column: int,
            component_type: str,
            by_component_type: bool = True,
            **kwargs,
    ):
        """"""
        logger.warning('To be deprecated')
        if by_component_type:
            self.delete(
                menu_path=menu_path,
                component_type=component_type,
                row=row, column=column,
            )
        else:
            self.delete(
                menu_path=menu_path,
                row=row, column=column,
                by_component_type=False,
            )

        m = getattr(self, component_type)
        return m(
            data=data,
            x=x, y=y,
            menu_path=menu_path,
            row=1, column=1,
            **kwargs
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
        cols: List[str] = [x] + y
        self._validate_table_data(data, elements=cols)
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[cols]  # keep only x and y

        df.rename(columns={x: 'xAxis'}, inplace=True)

        # Default
        option_modifications_temp = {
            "legend": {"type": "scroll"},
            "toolbox": {"orient": "vertical", "top": 20},
            'series': {'smooth': True}
        }

        # TODO this will be done in FE
        #  https://trello.com/c/GXRYHEsO/
        num_size: int = len(df[y].max())
        if num_size > 6:
            margin: int = 12 * (num_size - 6)  # 12 pixels by extra num
            option_modifications_temp["yAxis"] = {
                "axisLabel": {"margin": margin},
            }

        if option_modifications:
            if not option_modifications.get('legend'):
                option_modifications.update({"legend": {"type": "scroll"}})

            if not option_modifications.get('toolbox'):
                option_modifications['toolbox'] = {"orient": "vertical", "top": 20}
            elif not option_modifications.get('toolbox').get('orient'):
                option_modifications['toolbox'].update({"orient": "vertical", "top": 20})

            if not option_modifications.get('series'):
                option_modifications['series'] = {'smooth': True}
            elif not option_modifications.get('series').get('smooth'):
                option_modifications['series'].update({'smooth': True})

        else:
            option_modifications = option_modifications_temp

        # TODO we have two titles now, take a decision
        #  one in dataFields the other as field
        data_fields: Dict = self._set_data_fields(
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
            row=row, column=column,
            overwrite=True,
        )

    def _set_data_fields(
            self, title: str, subtitle: str,
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
            'chartOptions': chart_options,
        }

        if option_modifications:
            for k, v in option_modifications.items():
                if k == 'optionModifications':
                    data_fields[k] = v
                else:
                    data_fields['chartOptions'][k] = v

        return data_fields

    def table(
            self, data: Union[str, DataFrame, List[Dict]],
            menu_path: str, row: int, column: int,  # report creation
            title: Optional[str] = None,  # second layer
            filter_columns: Optional[List[str]] = None,
            sort_table_by_cols: Optional[List] = None,
            horizontal_scrolling: bool = False,
            overwrite: bool = True,
    ):
        """
        {
            "Product": null,
            "Monetary importance": {
                "field": "stringField2",
                "filterBy": ["High", "Medium", "Low"]
            },
            "Purchase soon": {
                "field": "stringField3",
                "filterBy": ["Yes", "No"]
            },
        }
        """

        def _calculate_table_filter_map() -> Dict[str, str]:
            """
            Example
            ----------------
            input
                filter_columns = ["Monetary importance"]

            output
                filters_map = {
                    'stringField1': 'Monetary importance',
                }
            """
            filters_map: Dict[str, str] = {}
            key_prefix_name: str = 'stringField'
            if filter_columns:
                for index, filter_column in enumerate(filter_columns):
                    filters_map[filter_column] = f'{key_prefix_name}{index + 1}'
                return filters_map
            else:
                return {}

        def _calculate_table_filter_fields() -> Dict[str, List[str]]:
            """
            Example
            ----------------
            input
                df
                    x, y, Monetary importance,
                    1, 2,                high,
                    2, 2,                high,
                   10, 9,                 low,
                    2, 1,                high,
                    4, 6,              medium,

                filter_columns = ["Monetary importance"]

            output
                filter_fields = {
                    'Monetary importance': ['high', 'medium', 'low'],
                }
            """
            filters: Dict[str, List[str]] = {}
            if filter_columns:
                for filter_column in filter_columns:
                    values: List[str] = df[filter_column].unique().tolist()

                    try:
                        assert len(values) <= 20
                    except AssertionError:
                        raise ValueError(
                            f'At maximum a table may have 20 different values in a filter | '
                            f'You provided {len(values)} | '
                            f'You provided {values}'
                        )
                    filters[filter_column] = values
                return filters
            else:
                return {}

        def _calculate_table_data_fields() -> Dict:
            """
            Example
            -------------
            input
                df
                    x, y, Monetary importance,
                    1, 2,                high,
                    2, 2,                high,
                   10, 9,                 low,
                    2, 1,                high,
                    4, 6,              medium,

                filters_map = {
                    'stringField1': 'Monetary importance',
                }

                filter_fields = {
                    'Monetary importance': ['high', 'medium', 'low'],
                }

            output
                {
                    "Product": null,
                    "Monetary importance": {
                        "field": "stringField1",
                        "filterBy": ["high", "medium", "low"]
                    },
                }
            """
            data_fields: Dict = {}
            cols: List[str] = df.columns
            for col in cols:
                if col in filter_fields:
                    data_fields[col] = {
                        'field': filter_map[col],
                        'filterBy': filter_fields[col],
                    }
                else:
                    data_fields[col] = None
            return json.dumps(data_fields)

        df: DataFrame = self._validate_data_is_pandarable(data)

        # This is for the responsive part of the application
        #  by default 6 is the maximum for average desktop screensize
        #  then it starts creating an horizontal scrolling
        if horizontal_scrolling:
            if len(df.columns) > 6:
                raise ValueError(
                    f'Tables with more than 6 columns are not allowed'
                )

        filter_map: Dict[str, str] = _calculate_table_filter_map()
        filter_fields: Dict[str, List[str]] = _calculate_table_filter_fields()

        app_type_name, path_name = self._clean_menu_path(menu_path=menu_path)
        d: Dict[str, Dict] = self._create_app_type_and_app(
            business_id=self.business_id,
            app_type_metadata={'name': app_type_name},
            app_metadata={},
        )
        app: Dict = d['app']
        app_id: str = app['id']

        order: int = self._get_component_order(
            app_id=app_id, path_name=path_name,
        )

        report_metadata: Dict[str, Any] = {
            'title': title,
            'grid': f'{row}, {column}',
            'path': path_name,
            'order': order,
        }

        report_metadata['dataFields'] = _calculate_table_data_fields()

        if overwrite:
            if not row or not column:
                raise ValueError(
                    'Row and Column must be specified to overwrite a report'
                )

            self.delete(
                menu_path=menu_path,
                row=row, column=column,
                by_component_type=False,
            )

        report: Dict = self._create_report(
            business_id=self.business_id,
            app_id=app_id,
            report_metadata=report_metadata,
        )
        report_id: str = report['id']

        report_entry_filter_fields: Dict[str, List[str]] = {
            filter_map[filter_name]: values
            for filter_name, values in filter_fields.items()
        }

        if sort_table_by_cols:
            df = df.sort_values(by=sort_table_by_cols, ascending=True)

        # We do not allow NaN values for report Entry
        df = df.fillna('')
        report_entries: List[Dict] = (
            self._convert_dataframe_to_report_entry(
                df=df, filter_map=filter_map,
                filter_fields=report_entry_filter_fields
            )
        )

        self._update_report_data(
            business_id=self.business_id,
            app_id=app_id,
            report_id=report_id,
            report_data=report_entries,
        )

    def html(
            self, html: str, menu_path: str,
            title: Optional[str] = None,
            row: Optional[int] = None,
            column: Optional[int] = None,
            order: Optional[int] = None,
    ):
        report_metadata: Dict = {
            'reportType': 'HTML',
            'order': order if order else 1,
            'title': title if title else '',
            'grid': f'{row}, {column}' if row else '1, 1',
        }

        return self._create_chart(
            data=[{'value': html}],
            menu_path=menu_path,
            row=row, column=column,
            report_metadata=report_metadata,
        )

    def iframe(
            self, menu_path: str, url: str,
            row: int, column: int,
            title: Optional[str] = None,
            height: Optional[int] = None,
            order: Optional[int] = None,
    ):
        report_metadata: Dict = {
            'reportType': 'IFRAME',
            'dataFields': {
                'url': url,
                'height': height if height else 600
            },
            'order': order if order else 1,
            'title': title if title else '',
            'grid': f'{row}, {column}',
        }

        return self._create_chart(
            data=[], menu_path=menu_path,
            row=row, column=column,
            report_metadata=report_metadata,
        )

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
        option_modifications: Dict[str, Any] = {'dataZoom': False}
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

    def horizontal_barchart(
            self, data: Union[str, DataFrame, List[Dict]],
            x: List[str], y: str,  # first layer
            menu_path: str, row: int, column: int,  # report creation
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[List[str]] = None,
    ):
        """Create a Horizontal barchart
        https://echarts.apache.org/examples/en/editor.html?c=bar-y-category
        """
        option_modifications: Dict[str, Any] = {
            'dataZoom': False,
            'xAxis': {'type': 'value'},
            'yAxis': {'type': 'category'},
            'optionModifications': {'yAxis': {'boundaryGap': True}},
        }
        return self._create_trend_chart(
            data=data, x=y, y=x, menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='bar',
            filters=filters,
        )

    def zero_centered_barchart(
            self, data: Union[str, DataFrame, List[Dict]],
            x: List[str], y: str,  # first layer
            menu_path: str, row: int, column: int,  # report creation
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[List[str]] = None,
    ):
        """Create a Horizontal barchart
        https://echarts.apache.org/examples/en/editor.html?c=bar-y-category
        """
        option_modifications: Dict[str, Any] = {
            'dataZoom': False,
            'xAxis': {
                'type': 'value',
                'position': 'top',
                'splitLine': {
                    'lineStyle': {'type': 'dashed'}
                }
            },
            'yAxis': {
                'type': 'category',
                'axisLine': {'show': False},
                'axisLabel': {'show': False},
                'axisTick': {'show': False},
                'splitLine': {'show': False},
            },
            'optionModifications': {'yAxis': {'boundaryGap': True}},
        }
        return self._create_trend_chart(
            data=data, x=y, y=x, menu_path=menu_path,
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
            'series': {
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
            },
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
            x: str, y: str,  # above_band_name: str, below_band_name: str,
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
            data=data, x=x, y=[y], menu_path=menu_path,
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
            x: str, y: str,  # above_band_name: str, below_band_name: str,
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
            data=data, x=x, y=[y], menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='scatter',
            filters=filters,
        )

    def stockline(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],  # first layer
            menu_path: str, row: int, column: int,  # report creation
            title: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[List[str]] = None,
    ):
        """"""
        self._validate_table_data(data, elements=[x] + y)
        df: DataFrame = self._validate_data_is_pandarable(data)
        data_fields: Dict = {
            "key": x_axis_name,
            "labels": {
                "key": x_axis_name,
                "value": y_axis_name,
                "hideKey": False,
                "hideValue": False
            },
            "values": y,
            "dataZoomX": True,
            "smooth": True,
            "symbol": "circle",
        }

        report_metadata: Dict = {
            'reportType': 'STOCKLINECHART',
            'grid': f'{row}, {column}',
            'title': title if title else '',
            'dataFields': data_fields,
        }

        return self._create_chart(
            data=df,
            menu_path=menu_path,
            row=row, column=column,
            report_metadata=report_metadata,
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
            data=data, x=x, y=y, menu_path=menu_path,
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
            x: str, y: List[str], z: str,  # first layer
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
            target_path: Optional[str] = None,
            set_title: Optional[str] = None,
            header: Optional[str] = None,
            footer: Optional[str] = None,
            color: Optional[str] = None,
            align: Optional[str] = None,
            multi_column: int = 4,
    ):
        """
        :param data:
        :param value:
        :param menu_path:
        :param row:
        :param column:
        :param target_path:
        :param set_title: the title of the set of indicators
        :param header:
        :param footer:
        :param color:
        :param align: to align center, left or right a component
        :param multi_column: how many indicators are allowed by column
        """

        def _set_indicator_columns(columns: int) -> Dict:
            if align:
                return {'dataFields': {'columns': columns, 'align': align}}
            else:
                return {'dataFields': {'columns': columns}}

        if align:
            try:
                assert align in ['center', 'left', 'right']
            except AssertionError:
                raise ValueError(
                    f'Align must be either "left", "center" or "right" '
                    f'| value passed {align}'
                )

        elements: List[str] = [header, footer, value, color, target_path]
        elements = [element for element in elements if element]

        self._validate_table_data(data, elements=elements)
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[elements]  # keep only x and y

        cols_to_rename: Dict[str, str] = {
            header: 'title',
            footer: 'description',
            value: 'value',
            color: 'color',
        }

        if target_path:
            cols_to_rename.update({target_path: 'targetPath'})

        cols_to_rename = {
            col_to_rename: v
            for col_to_rename, v in cols_to_rename.items()
            if col_to_rename in elements
        }
        df.rename(columns=cols_to_rename, inplace=True)

        report_metadata: Dict = {
            'reportType': 'INDICATORS',
            'grid': f'{row}, {column}',
            'title': set_title if set_title else ''
        }

        # TODO align is not working well yet
        # By default Shimoku assigns 4 indicators per row
        #  the following lines adjust it to the nature of the data
        #  and the multi_column variable
        len_df: int = len(df)
        if len_df < multi_column:
            columns: int = len_df
            data_fields = _set_indicator_columns(columns)
            report_metadata.update(data_fields)
        elif multi_column != 4:
            columns: int = multi_column
            data_fields = _set_indicator_columns(columns)
            report_metadata.update(data_fields)

        return self._create_chart(
            data=df,
            menu_path=menu_path,
            row=row, column=column,
            report_metadata=report_metadata,
        )

    def alert_indicator(
            self, data: Union[str, DataFrame, List[Dict]],
            value: str, target_path: str,
            menu_path: str, row: int, column: int,  # report creation
            set_title: Optional[str] = None,
            header: Optional[str] = None,
            footer: Optional[str] = None,
            color: Optional[str] = None,
            multi_column: int = 4,
    ):
        """"""
        elements: List[str] = [header, footer, value, color, target_path]
        elements = [element for element in elements if element]
        self._validate_table_data(data, elements=elements)
        return self.indicator(
            data=data, value=value,
            menu_path=menu_path, row=row, column=column,
            target_path=target_path,
            set_title=set_title,
            header=header,
            footer=footer, color=color,
            multi_column=multi_column,
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
            row=row, column=column,
            report_metadata=report_metadata,
        )

    def radar(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],  # first layer
            menu_path: str, row: int, column: int,  # report creation
            title: Optional[str] = None,  # second layer
            # subtitle: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[List[str]] = None,
    ):
        """Create a RADAR
        """
        self._validate_table_data(data, elements=[x] + y)
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[x] + y]  # keep only x and y
        df.rename(columns={x: 'name'}, inplace=True)
        data_fields: Dict = {
            'type': 'radar',
        }

        if option_modifications:
            data_fields['optionModifications'] = option_modifications

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
            row=row, column=column,
            report_metadata=report_metadata,
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
        self._validate_tree_data(data[0], vals=['name', 'value', 'children'])

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
            row=row, column=column,
            report_metadata=report_metadata,
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
        self._validate_tree_data(data[0], vals=['name', 'value', 'children'])

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
            row=row, column=column,
            report_metadata=report_metadata,
        )

    def sunburst(
            self, data: List[Dict],
            name: str, children: str, value: str,
            menu_path: str, row: int, column: int,  # report creation
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[List[str]] = None,
    ):
        """Create a Sunburst
        """
        self._validate_tree_data(data[0], vals=['name', 'children'])

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
            row=row, column=column,
            report_metadata=report_metadata,
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
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='candlestick',
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

        option_modifications: Dict = {
            "toolbox": {"orient": "horizontal", "top": 0},
        }

        return self._create_trend_chart(
            data=df, x=x, y=[y, value], menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='heatmap',
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
        df = df[[source, target, value]]  # keep only x and y
        df.rename(
            columns={
                source: 'source',
                target: 'target',
                value: 'value',
            },
            inplace=True,
        )

        report_metadata: Dict = {
            'title': title,
            'grid': f'{row}, {column}',
            'reportType': 'ECHARTS',
            'dataFields': {'type': 'sankey'},
        }

        if filters:
            raise NotImplementedError

        return self._create_chart(
            data=df, menu_path=menu_path,
            row=row, column=column,
            report_metadata=report_metadata,
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
                name: 'name',
                value: 'value',
            },
            inplace=True,
        )

        return self._create_trend_chart(
            data=df, x=name, y=[value], menu_path=menu_path,
            row=row, column=column,
            title=title, subtitle=subtitle,
            x_axis_name=x_axis_name,
            y_axis_name=y_axis_name,
            option_modifications=option_modifications,
            echart_type='funnel',
            filters=filters,
        )

    def gauge(
            self, data: Union[str, DataFrame, List[Dict]],
            name: str, value: str,
            menu_path: str, row: int, column: int,  # report creation
            title: Optional[str] = None,  # second layer
            # subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[List[str]] = None,
    ):
        """"""
        self._validate_table_data(data, elements=[name, value])
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[name, value]]  # keep only x and y
        df.rename(
            columns={
                name: 'name',
                value: 'value',
            },
            inplace=True,
        )

        data_fields: Dict = {
            'type': 'gauge',
        }
        if option_modifications:
            data_fields['optionModifications'] = option_modifications

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
            row=row, column=column,
            report_metadata=report_metadata,
        )

    def themeriver(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: str, name: str,  # first layer
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
            echart_type='themeriver',
            filters=filters,
        )

    def stacked_barchart(self):
        raise NotImplementedError
