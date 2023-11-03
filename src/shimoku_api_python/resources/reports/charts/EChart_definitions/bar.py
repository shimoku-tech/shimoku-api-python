from typing import TYPE_CHECKING, Optional, Union, List, Dict, Tuple
from pandas import DataFrame

from copy import deepcopy

from ..echart import get_common_echart_options, get_common_series_options

if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

import logging
from shimoku_api_python.execution_logger import logging_before_and_after

logger = logging.getLogger(__name__)


def thin_variant(y: List[str], series_options: Dict):
    len_y = len(y)
    dot_series_options = deepcopy(series_options)
    series_options['barWidth'] = 3
    series_options['barGap'] = '-100%'
    series_options['label'] = {'show': False}
    if len_y > 1:
        series_options['itemStyle']['opacity'] = 0.75
    series_options = len_y * [series_options]
    dot_series_options['type'] = 'scatter'
    dot_series_options['itemStyle']['opacity'] = 1
    dot_series_options['itemStyle']['borderWidth'] = 0
    dot_series_options['label'] = {'position': 'top', 'color': 'inherit'}
    series_options.append(dot_series_options)
    y = y + y
    return y, series_options


def shadow_variant(series_options: Dict):
    series_options['showBackground'] = True
    series_options['backgroundStyle'] = {'color': 'rgba(180, 180, 180, 0.2)'}
    series_options['label'] = {'position': 'top', 'color': 'inherit'}
    return series_options


def horizontal_clean_variant(common_options: Dict):
    common_options['xAxis'][0].update({
        'position': 'top',
        'axisLabel': {
            'rotate': -45,
        }
    })
    return common_options


def interpret_variant(variant: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not variant:
        return None, None
    variant = variant.split(' ')
    if len(variant) == 1:
        if variant[0] in ['thin', 'shadow']:
            return None, variant[0]
        elif variant[0] in ['clean', 'minimal']:
            return variant[0], None
        raise ValueError(f'Invalid variant: {variant}')
    elif len(variant) == 2 and variant[0] in ['clean', 'minimal']:
        return variant[0], variant[1]
    else:
        raise ValueError(f'Invalid variant: {variant}')


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def bar_chart(
        self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
        order: int, x: str, y: Optional[Union[List[str], str]] = None,
        rows_size: Optional[int] = None, cols_size: Optional[int] = None,
        padding: Optional[List[int]] = None, title: Optional[str] = None,
        x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
        show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None,
        variant: Optional[str] = None
):
    """ Create a bar chart """
    series_options = get_common_series_options()
    data_mapping_to_tuples = await self._choose_data(order, data=data)
    series_options['type'] = 'bar'
    clean, variant = interpret_variant(variant)

    if variant == 'thin':
        y = y if y else [k for k in data_mapping_to_tuples.keys() if k != x]
        y, series_options = thin_variant(y, series_options)
    elif variant == 'shadow':
        series_options = shadow_variant(series_options)

    await self._create_trend_chart(
        echart_options=get_common_echart_options(), variant=clean,
        series_options=series_options, option_modifications=option_modifications, axes=x, values=y,
        data_mapping_to_tuples=data_mapping_to_tuples,
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
        show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None,
        variant: Optional[str] = None
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
    clean, variant = interpret_variant(variant)
    if variant == 'thin':
        y = y if y else [k for k in data_mapping_to_tuples.keys() if k != x]
        len_y = len(y)
        y, series_options = thin_variant(y, series_options)
        series_options[-1]['stack'] = 'dot_stack'
        series_options[-1]['symbolSize'] = 5
        series_options[-1]['label']['position'] = 'left'
        series_options = series_options[:len_y] + [series_options[-1]] * (len_y - 1) + [deepcopy(series_options[-1])]
        series_options[-1]['label']['position'] = 'top'
        del series_options[-1]['symbolSize']
    else:
        len_y = len(y) if y else len(data_mapping_to_tuples.keys()) - 1
        if len_y > 1:
            series_options = [series_options] * (len_y - 1)
            series_options.append(deepcopy(series_options[-1]))
        else:
            series_options = [series_options]
        if variant == 'shadow':
            series_options[-1] = shadow_variant(series_options[-1])
        series_options[-1]['itemStyle']['borderRadius'] = [9, 9, 0, 0]

    await self._create_trend_chart(
        echart_options=get_common_echart_options(), variant=clean,
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
        show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None,
        variant: Optional[str] = None
):
    """ Create a zero centered bar chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    data_mapping_to_tuples = await self._choose_data(order, data=data)
    series_options['type'] = 'bar'
    common_options['xAxis'][0]['type'] = 'value'
    series_options['itemStyle']['borderRadius'] = [0, 0, 0, 0]
    del common_options['xAxis'][0]['data']
    common_options['yAxis'][0].update({
        'type': 'category',
        'data': '#set_data#',
    })
    clean, variant = interpret_variant(variant)
    if variant == 'thin':
        y = y if y else [k for k in data_mapping_to_tuples.keys() if k != x]
        y, series_options = thin_variant(y, series_options)
    elif variant == 'shadow':
        series_options = shadow_variant(series_options)

    await self._create_trend_chart(
        echart_options=common_options if not clean else horizontal_clean_variant(common_options),
        series_options=series_options, variant=clean,
        option_modifications=option_modifications, axes=x, values=y,
        data_mapping_to_tuples=data_mapping_to_tuples,
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
        show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None,
        variant: Optional[str] = None
):
    """ Create a horizontal bar chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    data_mapping_to_tuples = await self._choose_data(order, data=data)
    series_options['type'] = 'bar'
    common_options['xAxis'][0]['type'] = 'value'
    series_options['itemStyle']['borderRadius'] = [0, 9, 9, 0]
    del common_options['xAxis'][0]['data']
    common_options['yAxis'][0].update({
        'type': 'category',
        'data': '#set_data#',
    })
    clean, variant = interpret_variant(variant)
    if variant == 'thin':
        y = y if y else [k for k in data_mapping_to_tuples.keys() if k != x]
        y, series_options = thin_variant(y, series_options)
        series_options[-1]['label']['position'] = 'right'
    elif variant == 'shadow':
        series_options = shadow_variant(series_options)
        series_options['label']['position'] = 'right'

    await self._create_trend_chart(
        echart_options=common_options if not clean else horizontal_clean_variant(common_options),
        series_options=series_options, variant=clean,
        option_modifications=option_modifications, axes=x, values=y,
        data_mapping_to_tuples=data_mapping_to_tuples,
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
        show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None,
        variant: Optional[str] = None
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
    clean, variant = interpret_variant(variant)
    if variant == 'thin':
        y = y if y else [k for k in data_mapping_to_tuples.keys() if k != x]
        len_y = len(y)
        y, series_options = thin_variant(y, series_options)
        series_options[-1]['stack'] = 'dot_stack'
        series_options[-1]['symbolSize'] = 5
        series_options[-1]['label']['position'] = 'top'
        series_options = series_options[:len_y] + [series_options[-1]] * (len_y - 1) + [deepcopy(series_options[-1])]
        series_options[-1]['label']['position'] = 'right'
        del series_options[-1]['symbolSize']
    else:
        len_y = len(y) if y else len(data_mapping_to_tuples.keys()) - 1
        series_options = [series_options] * (len_y - 1)
        series_options.append(deepcopy(series_options[-1]))
        series_options[-1]['itemStyle']['borderRadius'] = [0, 9, 9, 0]
        if variant == 'shadow':
            series_options[-1] = shadow_variant(series_options[-1])
            series_options[-1]['label']['position'] = 'right'

    common_options['xAxis'][0]['type'] = 'value'
    del common_options['xAxis'][0]['data']
    common_options['yAxis'][0].update({
        'type': 'category',
        'data': '#set_data#',
    })

    await self._create_trend_chart(
        echart_options=common_options if not clean else horizontal_clean_variant(common_options),
        variant=clean, series_options=series_options, option_modifications=option_modifications,
        axes=x, values=y, data_mapping_to_tuples=data_mapping_to_tuples,
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values
    )
