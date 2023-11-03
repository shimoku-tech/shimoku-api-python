from typing import Optional, Union, List, TYPE_CHECKING, Dict, Tuple

from copy import deepcopy

import pandas as pd

from ..echart import get_common_echart_options, get_common_series_options
from shimoku_api_python.utils import ShimokuPalette
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

from pandas import DataFrame

import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def line_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, y: Optional[Union[List[str], str]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None,
    variant: Optional[str] = None
):
    """ Create a line chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options['type'] = 'line'
    common_options['yAxis'][0]['scale'] = True
    common_options['xAxis'][0]['boundaryGap'] = False
    if variant == 'minimal':
        series_options['itemStyle'] = {'opacity': 0}
        series_options['lineStyle'] = {'width': 3}

    await self._create_trend_chart(
        option_modifications=option_modifications,
        echart_options=common_options, series_options=series_options, variant=variant,
        axes=x, values=y, data_mapping_to_tuples=await self._choose_data(order, data),
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def area_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, y: Optional[Union[List[str], str]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None,
    variant: Optional[str] = None
):
    """ Create an area chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options.update({
        'type': 'line',
        'areaStyle': {'opacity': 0.5},
    })
    if variant == 'minimal':
        series_options['itemStyle'] = {'opacity': 0}
        series_options['areaStyle']['opacity'] = 0.2
        series_options['lineStyle'] = {'width': 3}

    common_options['xAxis'][0]['boundaryGap'] = False
    await self._create_trend_chart(
        option_modifications=option_modifications,
        echart_options=common_options, series_options=series_options,
        axes=x, values=y, data_mapping_to_tuples=await self._choose_data(order, data),
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values,
        variant=variant
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def stacked_area_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, y: Optional[Union[List[str], str]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    show_values: Optional[List[str]] = None, option_modifications: Optional[Dict] = None,
    variant: Optional[str] = None
):
    """ Create a stacked area chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options.update({
        'type': 'line',
        'areaStyle': {},
        'stack': 'stack',
        'itemStyle': {'borderRadius': [0, 0, 0, 0]},
    })
    common_options['xAxis'][0]['boundaryGap'] = False
    data_mapping_to_tuples = await self._choose_data(order, data)
    len_y = len(y) if y else len(data_mapping_to_tuples.keys())-1
    series_options = [series_options] * (len_y-1)
    series_options.append(deepcopy(series_options[-1]))
    series_options[-1]['itemStyle']['borderRadius'] = [9, 9, 0, 0]
    await self._create_trend_chart(
        option_modifications=option_modifications,
        echart_options=common_options, series_options=series_options,
        axes=x, values=y, data_mapping_to_tuples=data_mapping_to_tuples,
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values,
        variant=variant
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def predictive_line_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, y: Optional[Union[List[str], str]] = None,
    min_value_mark: Optional[str] = None, max_value_mark: Optional[str] = None,
    color_mark: str = 'rgba(255, 173, 177, 0.4)',
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    title: Optional[str] = None, rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, show_values: Optional[List[str]] = None,
    option_modifications: Optional[Dict] = None, variant: Optional[str] = None
):
    """ Create a predictive line chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options['type'] = 'line'
    common_options['yAxis'][0]['scale'] = True
    common_options['xAxis'][0]['boundaryGap'] = False
    series_options['markArea'] = {
        'itemStyle': {'color': color_mark},
        'data': [
            [
                {'name': 'Prediction', 'xAxis': min_value_mark},
                {'xAxis': max_value_mark},
            ]
        ]
    }
    await self._create_trend_chart(
        echart_options=common_options, series_options=series_options, option_modifications=option_modifications,
        axes=x, values=y, data_mapping_to_tuples=await self._choose_data(order, data),
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values, variant=variant
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def marked_line_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, marks: list,  y: Optional[Union[List[str], str]] = None,
    color_mark: str = 'rgba(255, 173, 177, 0.4)',
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    title: Optional[str] = None, rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, show_values: Optional[List[str]] = None,
    option_modifications: Optional[Dict] = None, variant: Optional[str] = None
):
    """ Create a predictive line chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options['type'] = 'line'
    common_options['yAxis'][0]['scale'] = True
    common_options['xAxis'][0]['boundaryGap'] = False
    series_options['markArea'] = {
        'itemStyle': {'color': color_mark},
        'data': [[
            {'name': name, 'xAxis': min_value_mark},
            {'xAxis': max_value_mark},
        ] for name, min_value_mark, max_value_mark in marks]
    }
    await self._create_trend_chart(
        echart_options=common_options, series_options=series_options, option_modifications=option_modifications,
        axes=x, values=y, data_mapping_to_tuples=await self._choose_data(order, data),
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values, variant=variant
    )


def calculate_segments(df: DataFrame, threshold: float, r: int, g: int, b: int):
    color_range = df['y'].max() - threshold
    df_as_dict = df.to_dict('records')
    segment = [None, None, None]
    segments = []
    for i in range(len(df_as_dict)):
        if df_as_dict[i]['y'] >= threshold and segment[0] is None:
            segment[0] = i-1 if i > 0 else 0
        elif (df_as_dict[i]['y'] < threshold or i == len(df_as_dict) - 1) and segment[0] is not None:
            if i < len(df_as_dict) - 1 and df_as_dict[i+1]['y'] >= threshold:
                continue
            segment[1] = i
            max_from_segment = max([val['y'] for val in df_as_dict[segment[0]:segment[1]]])
            color_alpha = 0.3 + (0.7 * (max_from_segment - threshold) / color_range if color_range > 0 else 0)
            segment[2] = f'rgba({r}, {g}, {b}, {color_alpha})'
            segments.append(tuple(segment))
            segment = [None, None, None]

    return segments


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def segmented_area_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, y: str, segments: Optional[list] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    default_color: Tuple[int, int, int] = (255, 0, 0), title: Optional[str] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, show_values: Optional[List[str]] = None,
    option_modifications: Optional[Dict] = None, variant: Optional[str] = None,
    top_area: bool = False, threshold: Optional[float] = None, labels: Optional[List[str]] = None
):
    """ Create a segmented area chart """
    if not isinstance(y, str):
        raise TypeError('y must be string')
    if threshold is not None and segments is not None:
        raise ValueError('You cannot specify both threshold and segments')
    if threshold is None and segments is None:
        raise ValueError('You must specify either threshold or segments')
    data_mappings_to_tuples = await self._choose_data(order, data)
    if isinstance(data, str):
        data = self._shared_data[data]
    df = pd.DataFrame(data)
    if threshold is not None:
        segments = calculate_segments(df, threshold, *default_color)

    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    common_options['xAxis'][0]['boundaryGap'] = False
    common_options['legend'] = {'show': False}
    del common_options['toolbox']['feature']['magicType']
    del common_options['toolbox']['bottom']
    common_options['toolbox']['top'] = "0px"
    common_options['dataZoom'] = [{'type': 'inside'}, {'type': 'slider'}] if variant is None else []
    pieces = []
    for segment in segments:
        if len(segment) == 2:
            r, g, b = default_color
            pieces.append({'gte': segment[0], 'lte': segment[1], 'color': f'rgba({r}, {g}, {b}, 0.75)'})
        elif len(segment) == 3:
            color = segment[2]
            if not isinstance(color, str):
                if not isinstance(color, tuple) or len(color) != 3:
                    log_error(logger, f'Color must be a string or a tuple of 3 elements, got {color}', ValueError)
                color = f'rgba({color[0]}, {color[1]}, {color[2]}, 0.75)'
            pieces.append({'gte': segment[0], 'lte': segment[1], 'color': color})
        else:
            raise ValueError('Segment must be a tuple of 2 or 3 elements')
    common_options['visualMap'] = {
        'type': 'piecewise',
        'show': False,
        'dimension': 0,
        'seriesIndex': 0,
        'pieces': pieces
    }
    series_options.update({
        'type': 'line',
        'emphasis': {'disabled': True},
        'areaStyle': {'origin': 'end' if top_area else 'start'},
        'itemStyle': {'opacity': 0},
    })

    series_options = [series_options, deepcopy(series_options)]
    del series_options[1]['areaStyle']

    if labels is None:
        labels = []
    if len(labels) < len(segments):
        labels += [''] * (len(segments) - len(labels))
    if len(labels) > len(segments):
        labels = labels[:len(segments)]

    series_options[1]['markArea'] = {
        'itemStyle': {'color': 'rgba(0, 0, 0, 0)'},
        'emphasis': {'disabled': True},
        'label': {
            'show': variant != 'minimal',
            'emphasis': {'disabled': True},
            'borderColor': f'rgba({default_color[0]}, {default_color[1]}, {default_color[2]}, 1)',
            'borderWidth': 1,
            'borderRadius': 5,
            'padding': [5, 5, 5, 5],
            'backgroundColor': f'rgba(0,0,0,0)'
        },
        'data': [[
            {'name': label, 'xAxis': marks_tuple[0]},
            {'xAxis': marks_tuple[1]},
        ] for label, marks_tuple in zip(labels, segments) if label]
    }

    await self._create_trend_chart(
        echart_options=common_options, series_options=series_options, option_modifications=option_modifications,
        axes=x, values=[y, y], data_mapping_to_tuples=data_mappings_to_tuples,
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, show_values=show_values, variant=variant
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def line_with_confidence_area_chart(
    self: 'PlotApi', data: Union[str, DataFrame, List[Dict]],
    order: int, x: str, lower: str, y: str, upper: str,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[str] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    percentages: bool = False, option_modifications: Optional[Dict] = None,
    variant: Optional[str] = None
):
    common_options = get_common_echart_options()
    del common_options['toolbox']['feature']['magicType']
    common_options.update({
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {
                'type': 'cross',
                'animation': False,
                'label': {
                    'backgroundColor': '#ccc',
                    'borderColor': '#aaa',
                    'borderWidth': 1,
                    'shadowBlur': 0,
                    'shadowOffsetX': 0,
                    'shadowOffsetY': 0,
                    'color': '#222'
                }
            },
        },
        'xAxis': [
            {
                'type': 'category',
                'fontFamily': 'Rubik',
                'nameLocation': 'middle',
                'boundaryGap': True,
                'nameGap': 35,
                'data': '#set_data#'
            }
        ],
        'yAxis': [
            {
                'type': 'value',
                'fontFamily': 'Rubik',
                'splitNumber': 3,
                'boundaryGap': True,
                'nameLocation': 'middle',
                'nameGap': 60,
                'axisLabel': {
                    'formatter': '{value}%' if percentages else '{value}'
                },
                'axisPointer': {
                    'label': {
                        'formatter': '{value}%' if percentages else '{value}'
                    }
                },
            },
        ],
    })
    series_options = [
        {
            'name': lower,
            'data': '#set_data#',
            'type': 'line',
            'lineStyle': {
                'color': '#000',
                'opacity': 0.1
            },
            'areaStyle': {
                'color': '#000',
                'opacity': 0.1,
                'origin': 'end'
            },
            'symbol': 'none'
        },
        {
            'name': upper,
            'data': '#set_data#',
            'silent': True,
            'type': 'line',
            'lineStyle': {
                 'color': '#000',
                 'opacity': 0.1
            },
            'areaStyle': {
                'color': '#000',
                'opacity': 0.1,
                'origin': 'start'
            },
            'symbol': 'none'
        },
        {
            'name': y,
            'data': '#set_data#',
            'type': 'line',
            'itemStyle': {
                'color': ShimokuPalette.CHART_C1.value
            },
            'emphasis': {
                'lineStyle': {
                    'color': ShimokuPalette.CHART_C1.value
                }
            },
            'showSymbol': False
        }
    ]

    await self._create_trend_chart(
        data_mapping_to_tuples=await self._choose_data(order, data), order=order, axes=x, values=[lower, upper, y],
        rows_size=rows_size, cols_size=cols_size, padding=padding, title=title, x_axis_names=x_axis_name,
        y_axis_names=y_axis_name, echart_options=common_options, series_options=series_options,
        option_modifications=option_modifications, variant=variant
    )


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def segmented_line_chart(
    self: 'PlotApi', order: int, x: str, y: Union[str, List[str]],
    data: Optional[Union[str, DataFrame, List[Dict]]],
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, title: Optional[str] = None,
    marking_lines: Optional[List[int]] = None,
    range_colors: Optional[List[str]] = None,
    option_modifications: Optional[Dict] = None,
    variant: Optional[str] = None
):
    """ Create a chart with bars and lines. """
    data_mappings_to_tuples = await self._choose_data(order, data)

    if isinstance(y, str):
        y = [y]

    if not marking_lines:
        marking_lines = [0]

    common_options = get_common_echart_options()
    common_options['xAxis'][0]['boundaryGap'] = False
    # Calculate the width of the visual map with the label of the marking line
    # ( lable  legend_ini - legend_end spaces for the legend colors)
    common_options['grid']['right'] = (
        max([len(f' {marking_lines[i + 1]}   {marking_lines[i]} - {marking_lines[i + 1]}        ')
            for i in range(0, len(marking_lines)-1)]
            ) * 6
    )
    common_options.update({
        'visualMap': {
            'top': 50,
            'right': 10,
            'itemHeight': 14 if variant != 'minimal' else 0,
            'showLabel': variant != 'minimal',
            'outOfRange': {'color': '#999'},
            'pieces': [{'min': marking_lines[i], 'max': marking_lines[i + 1]}
                       for i in range(len(marking_lines) - 1)] +
                      [{'min': marking_lines[-1]}],
        },
    })
    if range_colors:
        common_options['visualMap']['color'] = range_colors[::-1]
    series_options = get_common_series_options()
    series_options.update({
        'type': 'line',
        'color': ShimokuPalette.CHART_C5.value,
        'markLine': {
            'data': [{'yAxis': val} for val in marking_lines],
            'label': {'show': variant != 'minimal'},
            'itemStyle': {
                'color': ShimokuPalette.CHART_C5.value,
                'opacity': 0.5
            },
        }
    })

    await self._create_trend_chart(
        data_mapping_to_tuples=data_mappings_to_tuples, axes=x, values=y,
        echart_options=common_options, series_options=series_options,
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name,
        title=title, rows_size=rows_size, cols_size=cols_size, padding=padding,
        option_modifications=option_modifications, variant=variant
    )
