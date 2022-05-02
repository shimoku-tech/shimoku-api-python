""""""
from sys import stdout
from typing import List, Dict, Optional, Union, Tuple, Any, Iterable
import logging
import json
from itertools import product

import datetime as dt

import pandas as pd
from pandas import DataFrame

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

    @staticmethod
    def _validate_filters(filters: Dict) -> None:
        # Check the filters is built properly
        try:
            if filters.get('update_filter_type'):
                cols: List[str] = ['row', 'column', 'filter_cols', 'update_filter_type']
                assert sorted(list(filters.keys())) == sorted(cols)
            else:
                old_cols: List[str] = ['row', 'column', 'filter_cols']
                new_cols: List[str] = ['order', 'filter_cols']
                assert (
                    sorted(list(filters.keys())) == sorted(old_cols)
                    or
                    sorted(list(filters.keys())) == sorted(new_cols)
                )
        except AssertionError:
            raise KeyError(
                f'filters object must contain the keys'
                f'"exists", "row", "column", "filter_cols" | '
                f'Provided keys are: {list(filters.keys())}'
            )

    def _find_target_reports(
            self, menu_path: str,
            grid: Optional[str] = None,
            order: Optional[int] = None,
            component_type: Optional[str] = None,
            by_component_type: bool = True,
    ) -> List[Dict]:
        type_map = {
            'alert_indicator': 'INDICATORS',
            'indicator': 'INDICATORS',
            'table': None,
            'stockline': 'STOCKLINECHART',
            'html': 'HTML',
            'MULTIFILTER': 'MULTIFILTER',
        }
        if component_type in type_map.keys():
            component_type = type_map[component_type]
        else:
            component_type = 'ECHARTS'

        by_grid: bool = False
        if grid:
            by_grid = True
        elif order is not None:
            pass
        else:
            raise ValueError(
                'Row and Column or Order must be specified'
            )

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
        elif by_grid:  # Whatever is the reportType delete it
            target_reports: List[Dict] = [
                report
                for report in reports
                if (
                        report['path'] == path_name
                        and report['grid'] == grid
                )
            ]
        else:
            target_reports: List[Dict] = [
                report
                for report in reports
                if (
                        report['path'] == path_name
                        and report['order'] == order
                )
            ]

        return target_reports

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
            order: Optional[int] = None,
            rows_size: Optional[int] = None,
            cols_size: Optional[int] = None,
            padding: Optional[int] = None,
            overwrite: bool = True,
            real_time: bool = False,
    ) -> str:
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
        if order is not None and rows_size and cols_size:
            report_metadata['order'] = order
            report_metadata['sizeRows'] = rows_size
            report_metadata['sizeColumns'] = cols_size

        if padding:
            report_metadata['sizePadding'] = padding

        app_type_name, path_name = self._clean_menu_path(menu_path=menu_path)
        d: Dict[str, Dict] = self._create_app_type_and_app(
            business_id=self.business_id,
            app_type_metadata={'name': app_type_name},
            app_metadata={},
        )
        app: Dict = d['app']
        app_id: str = app['id']

        if order is not None:  # elif order fails when order = 0!
            kwargs = {'order': order}
        elif report_metadata.get('grid'):
            kwargs = {'grid': report_metadata.get('grid'), 'order': 0}
        else:
            raise ValueError(
                'Row and Column or Order must be specified to overwrite a report'
            )

        report_metadata.update({'path': path_name})
        report_metadata.update(kwargs)

        if report_metadata.get('dataFields'):
            report_metadata['dataFields'] = (
                json.dumps(report_metadata['dataFields'])
            )

        if overwrite:
            self.delete(
                menu_path=menu_path,
                by_component_type=False,
                **kwargs
            )

        report: Dict = self._create_report(
            business_id=self.business_id,
            app_id=app_id,
            report_metadata=report_metadata,
            real_time=real_time,
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

        return report_id

    def _create_trend_chart(
            self, echart_type: str,
            data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],  # first layer
            menu_path: str,
            row: Optional[int] = None,  # TODO to deprecate
            column: Optional[int] = None,    # TODO to deprecate
            order: Optional[int] = None,
            rows_size: Optional[int] = None,
            cols_size: Optional[int] = None,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
            overwrite: bool = True,
    ) -> str:
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
        }

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        if filters:
            raise NotImplementedError

        return self._create_chart(
            data=df,
            menu_path=menu_path, overwrite=overwrite,
            report_metadata=report_metadata, order=order,
            rows_size=rows_size, cols_size=cols_size, padding=padding,
        )

    def _create_multifilter_reports(
            self, data: Union[str, DataFrame, List[Dict]], filters: Dict,
    ) -> Iterable:
        """
        Create chunks of the data to create N reports for every filter combination
        """
        df: DataFrame = self._validate_data_is_pandarable(data)
        filter_cols: List[str] = filters['filter_cols']

        select_filter: Dict[str, str] = {
            v: f'Select{index + 1}'
            for index, v in enumerate(filter_cols)
        }

        # Create all combinations
        # https://stackoverflow.com/questions/18497604/combining-all-combinations-of-two-lists-into-a-dict-of-special-form
        d: Dict = {}
        for filter_name in filter_cols:
            d[filter_name] = df[filter_name].unique().tolist()

        filter_combinations = [
            dict(zip((list(d.keys())), row))
            for row in product(*list(d.values()))
        ]

        for filter_combination in filter_combinations:
            df_temp = df.copy()
            filter_element: Dict = {}
            for filter_, value in filter_combination.items():
                filter_element[select_filter[filter_]] = value
                df_temp = df_temp[df_temp[filter_] == value]

                if df_temp.empty:
                    break

            if df_temp.empty:
                continue

            # Get rid of NaN columns based on the filters
            df_temp = df_temp.dropna(axis=1)

            yield df_temp, filter_element

    def _update_filter_report(
            self, filter_row: Optional[int],
            filter_column: Optional[int],
            filter_order: Optional[int],
            filter_elements: List,
            menu_path: str,
            update_type: str = 'concat',
    ) -> None:
        """"""
        filter_reports: List[Dict] = (
            self._find_target_reports(
                menu_path=menu_path,
                grid=f'{filter_row}, {filter_column}',
                order=filter_order,
                component_type='MULTIFILTER',
                by_component_type=True,
            )
        )

        try:
            assert len(filter_reports) == 1
            filter_report = filter_reports[0]
        except AssertionError:
            raise ValueError(
                f'The Filter you are defining does not exist in the specified position | '
                f'{len(filter_reports)} | row {filter_row} | column {filter_column}'
            )

        filter_report_data: Dict = json.loads(
            filter_report['chartData']
        )

        # Here we append old and new reportId
        df_filter_report_data: pd.DataFrame = pd.DataFrame(filter_report_data)
        df_filter_elements: pd.DataFrame = pd.DataFrame(filter_elements)

        if update_type == 'concat':
            df_chart_data: pd.DataFrame = pd.concat([
                df_filter_report_data,
                df_filter_elements,
            ])
        elif update_type == 'append':
            df_chart_data: pd.DataFrame = pd.merge(
                df_filter_report_data, df_filter_elements,
                how='left', on=[
                    c
                    for c in df_filter_report_data.columns
                    if 'Select' in c
                ], suffixes=('_old', '_new')
            )
            df_chart_data['reportId'] = (
                df_chart_data['reportId_old']
                +
                df_chart_data['reportId_new']
            )
            df_chart_data.drop(
                columns=['reportId_old', 'reportId_new'],
                axis=1, inplace=True,
            )
        else:
            raise ValueError(
                f'update_type can only be "concat" or "append" | '
                f'Value provided is {update_type}'
            )

        chart_data: List[Dict] = df_chart_data.to_dict(orient='records')
        del df_chart_data

        report_metadata: Dict = {
            'reportType': 'MULTIFILTER',
            'grid': f'{filter_row}, {filter_column}',
            'title': '',
        }

        self._create_chart(
            data=chart_data,
            menu_path=menu_path,
            report_metadata=report_metadata,
            overwrite=True,
        )

    def _create_trend_charts_with_filters(
            self, data: Union[str, DataFrame, List[Dict]],
            filters: Dict, **kwargs,
    ):
        """"""
        filter_elements: List[Dict] = []
        self._validate_filters(filters=filters)

        # We are going to save all the reports one by one
        for df_temp, filter_element in (
                self._create_multifilter_reports(
                    data=data, filters=filters,
                )
        ):
            kwargs_: Dict = kwargs.copy()
            cols: List[str] = df_temp.columns
            kwargs_['y'] = [
                value for value in kwargs_['y']
                if value in cols
            ]
            report_id = self._create_trend_chart(
                data=df_temp, overwrite=False, **kwargs_,
            )
            filter_element['reportId'] = [report_id]
            filter_elements.append(filter_element)

        update_filter_type: Optional[str] = filters.get('update_filter_type')
        filter_row: Optional[int] = filters.get('row')
        filter_column: Optional[int] = filters.get('column')
        filter_order: Optional[int] = filters.get('order')

        if update_filter_type:
            # concat is to add new filter options
            # append is to add new reports to existing filter options
            try:
                assert update_filter_type in ['concat', 'append']
            except AssertionError:
                raise ValueError(
                    f'update_filter_type must be one of both: "concat" or "append" | '
                    f'Value provided: {update_filter_type}'
                )
            self._update_filter_report(
                filter_row=filter_row,
                filter_column=filter_column,
                filter_order=filter_order,
                filter_elements=filter_elements,
                menu_path=kwargs['menu_path'],
                update_type=update_filter_type,
            )
        else:
            report_metadata: Dict = {
                'reportType': 'MULTIFILTER',
                'title': '',
            }

            if filter_row and filter_column:
                report_metadata['grid'] = f'{filter_row}, {filter_column}'
            elif filter_order is not None:
                report_metadata['order'] = filter_order
            else:
                raise ValueError('Either row and column or order must be provided')

            self._create_chart(
                data=filter_elements,
                menu_path=kwargs['menu_path'],
                report_metadata=report_metadata,
                order=filter_order,
                overwrite=True,
            )

    def _create_trend_charts(
            self, data: Union[str, DataFrame, List[Dict]],
            filters: Optional[Dict], **kwargs,
    ):
        """
        Example
        -----------------
        filters: Dict = {
            'exists': False,
            'row': 1, 'column': 1,
            'filter_cols': [
                'seccion', 'frecuencia', 'region',
            ],
        }
        """
        if filters:
            self._create_trend_charts_with_filters(
                data=data, filters=filters, **kwargs
            )
        else:
            self._create_trend_chart(data=data, **kwargs)

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

    def append_data_to_trend_chart(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],
            component_type: str,
            menu_path: str,
            row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None,
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

        if row and column:
            target_reports: List[Dict] = (
                self._find_target_reports(
                    menu_path=menu_path, grid=f'{row}, {column}',
                    component_type=component_type,
                )
            )
        else:
            target_reports: List[Dict] = (
                self._find_target_reports(
                    menu_path=menu_path, order=order,
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
            self, menu_path: str,
            grid: Optional[str] = None,
            order: Optional[int] = None,
            row: Optional[int] = None,
            column: Optional[int] = None,
            component_type: Optional[str] = None,
            by_component_type: bool = True,
    ) -> None:
        """In cascade find the reports that match the query
        and delete them all
        """
        if grid:
            kwargs = {'grid': grid}
        elif order is not None:
            kwargs = {'order': order}
        elif row and column:
            kwargs = {'grid': f'{row}, {column}'}
        else:
            raise ValueError('Either Row and Column or Order must be specified')

        target_reports: List[Dict] = (
            self._find_target_reports(
                menu_path=menu_path,
                component_type=component_type,
                by_component_type=by_component_type,
                **kwargs,
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

    def table(
            self, data: Union[str, DataFrame, List[Dict]],
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            title: Optional[str] = None,  # second layer
            filter_columns: Optional[List[str]] = None,
            sort_table_by_col: Optional[Dict] = None,
            horizontal_scrolling: bool = False,
            overwrite: bool = True,
    ):
        """
        {
            "Product": null,
            "Monetary importance": {
                "field": "stringField2",
                "filterBy": ["High", "Medium", "Low"]
                "defaultOrder": "asc",
            },
            "Purchase soon": {
                "field": "stringField3",
                "filterBy": ["Yes", "No"]
            },
        }
        """

        def _calculate_table_extra_map() -> Dict[str, str]:
            """
            Example
            ----------------
            input
                filter_columns = ["Monetary importance"]
                sort_table_by_col = {'date': 'asc'}

            output
                filters_map = {
                    'stringField1': 'Monetary importance',
                    'stringField2': 'date',
                }
            """
            filters_map: Dict[str, str] = {}
            key_prefix_name: str = 'stringField'
            if sort_table_by_col:
                field_cols: List[str] = filter_columns + list(sort_table_by_col.keys())
            else:
                field_cols: List[str] = filter_columns

            if field_cols:
                for index, filter_column in enumerate(field_cols):
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
            filter_fields_: Dict[str, List[str]] = {}
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
                    filter_fields_[filter_column] = values
                return filter_fields_
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
            cols: List[str] = df.columns.tolist()
            if sort_table_by_col:
                cols_to_sort_by: List[str] = list(sort_table_by_col.keys())
            else:
                cols_to_sort_by: List[str] = []

            for col in cols:
                if col in filter_fields:
                    data_fields[col] = {
                        'field': extra_map[col],
                        'filterBy': filter_fields[col],
                    }
                else:
                    data_fields[col] = None

                if col in cols_to_sort_by:
                    if data_fields:
                        if data_fields[col]:
                            data_fields[col].update(
                                {
                                    'field': extra_map[col],
                                    "defaultOrder": sort_table_by_col[col],
                                }
                            )
                        else:
                            data_fields[col] = {
                                'field': extra_map[col],
                                "defaultOrder": sort_table_by_col[col],
                            }
                    else:
                        data_fields[col] = {
                            'field': extra_map[col],
                            "defaultOrder": sort_table_by_col[col],
                        }

            return json.dumps(data_fields)

        df: DataFrame = self._validate_data_is_pandarable(data)

        if sort_table_by_col:
            try:
                assert len(sort_table_by_col) == 1
            except AssertionError:
                raise ValueError(
                    f'Currently we can only sort tables by one column '
                    f'You passed {len(sort_table_by_col)} columns'
                )

        # This is for the responsive part of the application
        #  by default 6 is the maximum for average desktop screensize
        #  then it starts creating an horizontal scrolling
        if horizontal_scrolling:
            if len(df.columns) > 6:
                raise ValueError(
                    f'Tables with more than 6 columns are not allowed'
                )

        extra_map: Dict[str, str] = _calculate_table_extra_map()
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
            'path': path_name,
            'order': order,
            'dataFields': _calculate_table_data_fields(),
        }

        if row and column:
            report_metadata['grid']: str = f'{row}, {column}'

        if overwrite:
            if not row and not column and not order:
                raise ValueError(
                    'Row, Column or Order must be specified to overwrite a report'
                )

            if report_metadata.get('grid'):
                self.delete(
                    menu_path=menu_path,
                    grid=report_metadata.get('grid'),
                    by_component_type=False,
                )
            else:
                self.delete(
                    menu_path=menu_path,
                    order=order,
                    by_component_type=False,
                )

        report: Dict = self._create_report(
            business_id=self.business_id,
            app_id=app_id,
            report_metadata=report_metadata,
        )
        report_id: str = report['id']

        report_entry_filter_fields: Dict[str, List[str]] = {
            extra_map[extra_name]: values
            for extra_name, values in filter_fields.items()
        }

        # We do not allow NaN values for report Entry
        df = df.fillna('')
        report_entries: List[Dict] = (
            self._convert_dataframe_to_report_entry(
                df=df, filter_map=extra_map,
                sort_table_by_col=sort_table_by_col,
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
            row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[str] = None,
    ):
        report_metadata: Dict = {
            'reportType': 'HTML',
            'order': order if order else 1,
            'title': title if title else '',
        }

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=[{'value': html}],
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def iframe(
            self, menu_path: str, url: str,
            row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[str] = None,
            title: Optional[str] = None,
            height: Optional[int] = None,
    ):
        report_metadata: Dict = {
            'reportType': 'IFRAME',
            'dataFields': {
                'url': url,
                'height': height if height else 600
            },
            'order': order if order else 1,
            'title': title if title else '',
        }

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=[],
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def bar(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],  # first layer
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
    ):
        """Create a barchart
        """

        # TODO this only works for single bar:
        """
        'xAxis': {
            'axisLabel': {
                'inside': True,
                'color': '#ffffff'
            },
            'axisTick': {
                'show': False
            }
        },
        'color': '#002FD8',  # put multicolor
        """

        option_modifications: Dict[str, Any] = {
            'dataZoom': False,
            'optionModifications': {
                'series': {
                    'itemStyle': {
                        'borderRadius': [9, 9, 0, 0]
                    }
                },
                # 'color': '#002FD8',  # TODO put multicolor
                'emphasis': {
                    'itemStyle': {'color': '#29D86F'}
                },
            }
        }

        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=x, y=y,
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='bar',
            )
        )

    def horizontal_barchart(
            self, data: Union[str, DataFrame, List[Dict]],
            x: List[str], y: str,  # first layer
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
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
        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=x, y=y,
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='bar',
            )
        )

    def zero_centered_barchart(
            self, data: Union[str, DataFrame, List[Dict]],
            x: List[str], y: str,  # first layer
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
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
        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=x, y=y,
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='bar',
            )
        )

    def line(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],  # first layer
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # thid layer
            filters: Optional[Dict] = None,  # thid layer
    ):
        """"""
        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=x, y=y,
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='line',
            )
        )

    def predictive_line(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],  # first layer
            menu_path: str,
            min_value_mark: Any, max_value_mark: Any,
            color_mark: str = 'rgba(255, 173, 177, 0.4)',
            row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            filters: Optional[Dict] = None,
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
            'optionModifications': {
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
        }

        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=x, y=y,
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='line',
            )
        )

    def line_with_confidence_area(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: str,  # above_band_name: str, below_band_name: str,
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            filters: Optional[Dict] = None,
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

        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=x, y=[y],
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='line',
            )
        )

    def scatter_with_confidence_area(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: str,  # above_band_name: str, below_band_name: str,
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            filters: Optional[Dict] = None,
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
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
    ):
        """"""
        self._validate_table_data(data, elements=[x] + y)
        df: DataFrame = self._validate_data_is_pandarable(data)
        data_fields: Dict = {
            "key": x,
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
            'title': title if title else '',
            'dataFields': data_fields,
        }

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def scatter(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],  # first layer
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
    ):
        """"""
        try:
            assert 2 <= len(y) <= 3
        except Exception:
            raise ValueError(f'y provided has {len(y)} it has to have 2 or 3 dimensions')

        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=x, y=y,
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='scatter',
            )
        )

    def bubble_chart(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str], z: str,  # first layer
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,  # to create filters
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
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            target_path: Optional[str] = None,
            set_title: Optional[str] = None,
            header: Optional[str] = None,
            footer: Optional[str] = None,
            color: Optional[str] = None,
            align: Optional[str] = None,
            multi_column: int = 4,
            real_time: bool = False,
    ):
        """
        :param data:
        :param value:
        :param menu_path:
        :param row:
        :param column:
        :param order:
        :param rows_size:
        :param cols_size:
        :param padding:
        :param target_path:
        :param set_title: the title of the set of indicators
        :param header:
        :param footer:
        :param color:
        :param align: to align center, left or right a component
        :param multi_column: how many indicators are allowed by column
        :param real_time:
        """
        mandatory_elements: List[str] = [
            header, value, target_path,
        ]
        mandatory_elements = [element for element in mandatory_elements if element]
        extra_elements: List[str] = [footer, color, align]
        extra_elements = [element for element in extra_elements if element]

        self._validate_table_data(data, elements=mandatory_elements)
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[mandatory_elements + extra_elements]  # keep only x and y

        cols_to_rename: Dict[str, str] = {
            header: 'title',
            footer: 'description',
            value: 'value',
            color: 'color',
            align: 'align',
        }

        if target_path:
            cols_to_rename.update({target_path: 'targetPath'})

        cols_to_rename = {
            col_to_rename: v
            for col_to_rename, v in cols_to_rename.items()
            if col_to_rename in mandatory_elements + extra_elements
        }
        df.rename(columns=cols_to_rename, inplace=True)
        for extra_element in extra_elements:
            if extra_element == 'align':
                df['align'] = df['align'].fillna('right')
            elif extra_element == 'color':
                df['color'] = df['color'].fillna('black')
            elif extra_element == 'description':
                df['description'] = df['description'].fillna('')
            else:
                raise ValueError(f'{extra_element} is not solved')

        report_metadata: Dict = {
            'reportType': 'INDICATORS',
            'title': set_title if set_title else ''
        }

        # TODO align is not working well yet
        # By default Shimoku assigns 4 indicators per row
        #  the following lines adjust it to the nature of the data
        #  and the multi_column variable
        len_df: int = len(df)
        columns: int = 4
        if len_df < multi_column:
            columns: int = len_df
        elif multi_column != 4:
            columns: int = multi_column

        data_fields: Dict = {'dataFields': {'columns': columns}}
        report_metadata.update(data_fields)

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
            real_time=real_time,
        )

    def alert_indicator(
            self, data: Union[str, DataFrame, List[Dict]],
            value: str, target_path: str,
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
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
            order=order, cols_size=cols_size, rows_size=rows_size, padding=padding,
            target_path=target_path,
            set_title=set_title,
            header=header,
            footer=footer, color=color,
            multi_column=multi_column,
        )

    def pie(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: str,  # first layer
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
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
        }

        if filters:
            raise NotImplementedError

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def radar(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: List[str],  # first layer
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            # subtitle: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
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
        }

        if filters:
            raise NotImplementedError

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def tree(
            self, data: Union[str, List[Dict]],
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
    ):
        """Create a Tree
        """
        self._validate_tree_data(data[0], vals=['name', 'value', 'children'])

        report_metadata: Dict = {
            'reportType': 'ECHARTS',
            'dataFields': {'type': 'tree'},
            'title': title,
        }

        if filters:
            raise NotImplementedError

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def treemap(
            self, data: Union[str, List[Dict]],
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
    ):
        """Create a Treemap
        """
        self._validate_tree_data(data[0], vals=['name', 'value', 'children'])

        report_metadata: Dict = {
            'title': title,
            'reportType': 'ECHARTS',
            'dataFields': {'type': 'treemap'},
        }

        if filters:
            raise NotImplementedError

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def sunburst(
            self, data: List[Dict],
            name: str, children: str, value: str,
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
    ):
        """Create a Sunburst
        """
        self._validate_tree_data(data[0], vals=['name', 'children'])

        report_metadata: Dict = {
            'reportType': 'ECHARTS',
            'title': title,
            'dataFields': {'type': 'sunburst'},
        }

        if filters:
            raise NotImplementedError

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def candlestick(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str,
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
    ):
        """"""
        y = ['open', 'close', 'highest', 'lowest']

        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=x, y=y,
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='candlestick',
            )
        )

    def heatmap(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: str, value: str,
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
    ):
        """"""
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[x, y, value]]  # keep only x and y
        df.rename(columns={x: 'xAxis', y: 'yAxis', value: 'value'}, inplace=True)

        option_modifications: Dict = {
            "toolbox": {"orient": "horizontal", "top": 0},
        }

        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=x, y=[y, value],
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='heatmap',
            )
        )

    def cohort(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: str, value: str,
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            filters: Optional[Dict] = None,
    ):
        """"""
        df: DataFrame = self._validate_data_is_pandarable(data)
        df = df[[x, y, value]]  # keep only x and y
        df.rename(columns={x: 'xAxis', y: 'yAxis', value: 'value'}, inplace=True)

        option_modifications: Dict = {
            "toolbox": {"orient": "horizontal", "top": 0},
            "xAxis": {"axisLabel": {"margin": '10%'}},
            'optionModifications': {
                'grid': {
                    'bottom': '20%',
                    # 'top': '10%'
                },
                "visualMap": {
                    'calculable': True,
                    "inRange": {
                        "color": ['#cfb1ff', '#0000ff']
                    },
                },
            },
        }

        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=x, y=[y, value],
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='heatmap',
            )
        )

    def predictive_cohort(self):
        """"""
        raise NotImplementedError

    def sankey(
            self, data: Union[str, DataFrame, List[Dict]],
            source: str, target: str, value: str,
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
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
            'reportType': 'ECHARTS',
            'dataFields': {'type': 'sankey'},
        }

        if filters:
            raise NotImplementedError

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def funnel(
            self, data: Union[str, DataFrame, List[Dict]],
            name: str, value: str,
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
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

        return self._create_trend_charts(
            data=data, filters=filters,
            **dict(
                x=name, y=[value],
                menu_path=menu_path, row=row, column=column,
                order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
                title=title, subtitle=subtitle,
                x_axis_name=x_axis_name,
                y_axis_name=y_axis_name,
                option_modifications=option_modifications,
                echart_type='funnel',
            )
        )

    def speed_gauge(
            self, data: Union[str, DataFrame, List[Dict]],
            name: str, value: str,
            menu_path: str,
            min: int, max: int,
            row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            # subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
    ) -> str:
        """
        option = {
          series: [
            {
              type: 'gauge',
              startAngle: 190,
              endAngle: -10,
              min: 0,
              max: 80,
              pointer: {
                show: true
              },
              progress: {
                show: true,
                overlap: false,
                roundCap: true,
                clip: false,
                itemStyle: {
                  borderWidth: 0,
                  borderColor: '#464646'
                }
              },
              axisLine: {
                lineStyle: {
                  width: 10
                }
              },
              splitLine: {
                show: true,
                distance: 0,
                length: 5
              },
              axisTick: {
                show: true
              },
              axisLabel: {
                show: true,
                distance: 30
              },
              data: gaugeData,
              title: {
                fontSize: 14,
                offsetCenter: ['0%', '30%'],
              },
              anchor: {
                show: true,
                showAbove: true,
                size: 25,
                itemStyle: {
                  borderWidth: 10
                }
              },
              detail: {
                bottom: 10,
                width: 10,
                height: 14,
                fontSize: 14,
                color: 'auto',
                borderRadius: 20,
                borderWidth: 0,
                formatter: '{value}%',
                offsetCenter: [0, '45%']
              }
            }
          ]
        }
        """
        self._validate_table_data(data, elements=[name, value])
        df: DataFrame = self._validate_data_is_pandarable(data)
        title: str = (
            title if title
            else f'{df["name"].to_list()[0]}: {df["value"].to_list()[0]}'
        )
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
            'optionModifications': {
                'series': {
                    'startAngle': 190,
                    'endAngle': -10,
                    'min': min,
                    'max': max,
                    'pointer': {
                        'show': True
                    },
                    'progress': {
                        'show': True,
                        'overlap': False,
                        'roundCap': True,
                        'clip': False,
                        'itemStyle': {
                            'borderWidth': 0,
                            'borderColor': '#464646'
                        }
                    },
                    'axisLine': {
                        'lineStyle': {
                            'width': 10
                        }
                    },
                    'splitLine': {
                        'show': True,
                        'distance': 0,
                        'length': 5
                    },
                    'axisTick': {
                        'show': True,
                    },
                    'axisLabel': {
                        'show': True,
                        'distance': 30
                    },
                    'title': {
                        'show': False,
                    },
                    'anchor': {
                        'show': True,
                        'showAbove': True,
                        'size': 25,
                        'itemStyle': {
                            'borderWidth': 10
                        }
                    },
                    'detail': {
                        'show': False,
                    }
                },
            },
        }

        if option_modifications:
            raise NotImplementedError

        report_metadata: Dict = {
            'reportType': 'ECHARTS',
            'dataFields': data_fields,
            'title': title,
        }

        if filters:
            raise NotImplementedError

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def ring_gauge(
            self, data: Union[str, DataFrame, List[Dict]],
            name: str, value: str,
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            # subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
    ) -> str:
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
        }

        if filters:
            raise NotImplementedError

        if row and column:
            report_metadata['grid'] = f'{row}, {column}'

        return self._create_chart(
            data=data,
            menu_path=menu_path,
            order=order, rows_size=rows_size, cols_size=cols_size, padding=padding,
            report_metadata=report_metadata,
        )

    def themeriver(
            self, data: Union[str, DataFrame, List[Dict]],
            x: str, y: str, name: str,  # first layer
            menu_path: str, row: Optional[int] = None, column: Optional[int] = None,  # report creation
            order: Optional[int] = None, rows_size: Optional[int] = None, cols_size: int = 12,
            padding: Optional[List[int]] = None,
            title: Optional[str] = None,  # second layer
            subtitle: Optional[str] = None,
            x_axis_name: Optional[str] = None,
            y_axis_name: Optional[str] = None,
            option_modifications: Optional[Dict] = None,  # third layer
            filters: Optional[Dict] = None,
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
