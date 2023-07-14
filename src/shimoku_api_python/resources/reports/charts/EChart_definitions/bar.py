from typing import TYPE_CHECKING, Optional, Union, List, Dict
from pandas import DataFrame

from copy import deepcopy

from ..echart import get_common_echart_options, get_common_series_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def bar_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, y: Optional[Union[List[str], str]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None
):
    """ Create a bar chart """
    series_options = get_common_series_options()
    series_options['type'] = 'bar'
    await self._create_trend_chart(
        echart_options=get_common_echart_options(), series_options=series_options,
        option_modifications=option_modifications, axes=x, values=y,
        data_mapping_to_tuples=await self._choose_data(order, data),
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def stacked_bar_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, y: Optional[Union[List[str], str]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None
):
    """ Create a stacked bar chart """
    series_options = get_common_series_options()
    series_options.update({
        'type': 'bar',
        'areaStyle': {},
        'stack': 'stack',
        'itemStyle': {'borderRadius': [0, 0, 0, 0]},
    })
    data_mapping_to_tuples = await self._choose_data(order, data=data)

    len_y = len(y) if y else len(data_mapping_to_tuples.keys())-1
    series_options = [series_options] * (len_y-1)
    series_options.append(deepcopy(series_options[-1]))
    series_options[-1]['itemStyle']['borderRadius'] = [9, 9, 0, 0]

    await self._create_trend_chart(
        echart_options=get_common_echart_options(),
        axes=x, values=y, data_mapping_to_tuples=data_mapping_to_tuples,
        series_options=series_options, option_modifications=option_modifications,
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def zero_centered_bar_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, y: Optional[Union[List[str], str]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None
):
    """ Create a zero centered bar chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options['type'] = 'bar'
    common_options['xAxis'][0]['type'] = 'value'
    series_options['itemStyle']['borderRadius'] = [0, 0, 0, 0]
    del common_options['xAxis'][0]['data']
    common_options['yAxis'][0].update({
        'type': 'category',
        'data': '#set_data#',
    })
    await self._create_trend_chart(
        echart_options=common_options, series_options=series_options,
        option_modifications=option_modifications, axes=x, values=y,
        data_mapping_to_tuples=await self._choose_data(order, data),
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def horizontal_bar_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, y: Optional[Union[List[str], str]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None
):
    """ Create a horizontal bar chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options['type'] = 'bar'
    common_options['xAxis'][0]['type'] = 'value'
    series_options['itemStyle']['borderRadius'] = [0, 9, 9, 0]
    del common_options['xAxis'][0]['data']
    common_options['yAxis'][0].update({
        'type': 'category',
        'data': '#set_data#',
    })

    await self._create_trend_chart(
        echart_options=common_options, series_options=series_options,
        option_modifications=option_modifications, axes=x, values=y,
        data_mapping_to_tuples=await self._choose_data(order, data),
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def stacked_horizontal_bar_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, y: Optional[Union[List[str], str]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None
):
    """ Create a stacked horizontal bar chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options.update({
        'type': 'bar',
        'areaStyle': {},
        'stack': 'stack',
        'itemStyle': {'borderRadius': [0, 0, 0, 0]},
    })
    data_mapping_to_tuples = await self._choose_data(order, data=data)
    len_y = len(y) if y else len(data_mapping_to_tuples.keys())-1
    series_options = [series_options] * (len_y-1)
    series_options.append(deepcopy(series_options[-1]))
    series_options[-1]['itemStyle']['borderRadius'] = [0, 9, 9, 0]
    common_options['xAxis'][0]['type'] = 'value'
    del common_options['xAxis'][0]['data']
    common_options['yAxis'][0].update({
        'type': 'category',
        'data': '#set_data#',
    })

    await self._create_trend_chart(
        option_modifications=option_modifications,
        echart_options=common_options, series_options=series_options,
        axes=x, values=y, data_mapping_to_tuples=data_mapping_to_tuples,
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values
    )



