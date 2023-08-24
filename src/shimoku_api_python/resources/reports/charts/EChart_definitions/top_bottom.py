from typing import Optional, Union, List, TYPE_CHECKING, Dict

from copy import deepcopy

from ..echart import get_common_echart_options, get_common_series_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

from pandas import DataFrame

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def top_bottom_area_charts(
    self: 'PlotApi',
    data: Union[str, DataFrame, List[Dict]], order: Optional[int] = None,
    x: str = 'x', top_names: Optional[List[str]] = None, bottom_names: Optional[List[str]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[str] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, top_axis_name: Optional[str] = None,
    bottom_axis_name: Optional[str] = None, option_modifications: Optional[Dict] = None,
    variant: Optional[str] = None
):
    if top_names is None:
        top_names = ['up']

    if bottom_names is None:
        bottom_names = ['down']

    common_options = get_common_echart_options()
    series_options = get_common_series_options()

    common_options.update({
        'xAxis': [
            {
                'name': x_axis_name if x_axis_name else "",
                'type': 'category',
                'boundaryGap': True,
                'axisLine': {'onZero': False},
                'data': '#set_data#'
            }
        ],
        'yAxis': [
            {
                'name': top_axis_name if top_axis_name else "",
                'type': 'value'
            },
            {
                'name': bottom_axis_name if bottom_axis_name else "",
                'nameLocation': 'start',
                'alignTicks': True,
                'type': 'value',
                'inverse': True
            }
        ],
    })
    series_options.update(
        {
            'type': 'line',
            'areaStyle': {'opacity': 0.5},
            'lineStyle': {
                'width': 1
            },
            'emphasis': {
                'focus': 'series'
            },
            'markArea': {
                'silent': True,
                'itemStyle': {
                    'opacity': 0.3
                },
            },
        }
    )
    series = []
    for name in bottom_names:
        aux_series_options = deepcopy(series_options)
        aux_series_options['name'] = name
        series.append(aux_series_options)

    for name in top_names:
        aux_series_options = deepcopy(series_options)
        aux_series_options['name'] = name
        aux_series_options['yAxisIndex'] = 1
        series.append(aux_series_options)

    await self._create_trend_chart(
        data_mapping_to_tuples=await self._choose_data(order, data), order=order, axes=x, values=bottom_names+top_names,
        rows_size=rows_size, cols_size=cols_size, padding=padding, title=title, x_axis_names=x_axis_name,
        y_axis_names=[bottom_axis_name, top_axis_name], echart_options=common_options, series_options=series,
        option_modifications=option_modifications, variant=variant
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def top_bottom_line_charts(
    self: 'PlotApi',
    data: Union[str, DataFrame, List[Dict]], order: int,
    x: str, top_names: Optional[List[str]] = None, bottom_names: Optional[List[str]] = None,
    rows_size: int = 4, cols_size: Optional[int] = None,
    padding: Optional[str] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, top_axis_name: Optional[str] = None,
    bottom_axis_name: Optional[str] = None, option_modifications: Optional[Dict] = None,
):
    if top_names is None:
        top_names = ['up']

    if bottom_names is None:
        bottom_names = ['down']

    common_options = get_common_echart_options()
    series_options = get_common_series_options()

    common_options.update({
        'grid': [
            {
                'left': 60,
                'right': 50,
                'height': '35%'
            },
            {
                'left': 60,
                'right': 50,
                'top': '55%',
                'height': '35%'
            }
        ],
        'xAxis': [
            {
                'name': x_axis_name if x_axis_name else "",
                'type': 'category',
                'boundaryGap': False,
                'axisLine': {'onZero': True},
                'data': '#set_data#',
                'label': {'show': False}
            },
            {
                'gridIndex': 1,
                'type': 'category',
                'boundaryGap': False,
                'axisLine': {'onZero': True},
                'position': 'top',
                'data': '#set_data#'
            }
        ],
        'yAxis': [
            {
                'name': top_axis_name if top_axis_name else "",
                'type': 'value',
                'nameLocation': 'middle',
                'nameGap': 40,
            },
            {
                'gridIndex': 1,
                'name': bottom_axis_name if bottom_axis_name else "",
                'alignTicks': True,
                'type': 'value',
                'inverse': True,
                'nameLocation': 'middle',
                'nameGap': 40,
            }
        ],
    })
    series_options.update(
        {
            'type': 'line',
            'lineStyle': {
                'width': 1
            },
            'emphasis': {
                'focus': 'series'
            },
            'markArea': {
                'silent': True,
                'itemStyle': {
                    'opacity': 0.3
                },
            },
        }
    )
    series = []
    for name in bottom_names:
        aux_series_options = deepcopy(series_options)
        aux_series_options['name'] = name
        series.append(aux_series_options)

    for name in top_names:
        aux_series_options = deepcopy(series_options)
        aux_series_options['name'] = name
        aux_series_options['yAxisIndex'] = 1
        aux_series_options['xAxisIndex'] = 1
        series.append(aux_series_options)

    await self._create_trend_chart(
        data_mapping_to_tuples=await self._choose_data(order, data),
        order=order, axes=[x, x], values=bottom_names + top_names, option_modifications=option_modifications,
        rows_size=rows_size, cols_size=cols_size, padding=padding, title=title, x_axis_names=x_axis_name,
        y_axis_names=[bottom_axis_name, top_axis_name], echart_options=common_options, series_options=series,
    )
