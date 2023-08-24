from typing import Optional, Dict,  Union, List, TYPE_CHECKING
from math import floor, ceil, log10
from pandas import DataFrame
from copy import deepcopy

from ..echart import get_common_echart_options, get_common_series_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager
from shimoku_api_python.utils import validate_data_is_pandarable, ShimokuPalette

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def line_and_bar_charts(
    self: 'PlotApi', order: int, x: str,
    data: Optional[Union[str, DataFrame, List[Dict]]],
    bar_names: Optional[List[str]] = None,
    line_names: Optional[List[str]] = None,
    x_axis_name: Optional[str] = None,
    bar_axis_name: Optional[str] = None, bar_suffix: Optional[str] = None,
    line_axis_name: Optional[str] = None, line_suffix: Optional[str] = None,
    title: Optional[str] = None, rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None,
    option_modifications: Optional[Dict] = None,
    variant: Optional[str] = None
):
    """ Create a chart with bars and lines. """
    data_mappings_to_tuples = await self._choose_data(order, data)
    if isinstance(data, str):
        data = self._shared_data[data]

    if bar_names is None:
        bar_names = ['bar']

    if line_names is None:
        line_names = ['line']

    df: DataFrame = validate_data_is_pandarable(data)
    max_bars = df[bar_names].max().max()
    pow_10 = floor(log10(abs(max_bars)))
    max_bars = ceil(max_bars / 10 ** pow_10) * 10 ** pow_10
    bar_interval = abs(max_bars) / (5 if 1000 > max_bars > 0.01 else 10)

    longest_value_bars = max(len(str(max_bars)), len(str(bar_interval)))

    max_lines = df[line_names].max().max()
    pow_10 = floor(log10(abs(max_lines)))
    max_lines = ceil(max_lines / 10 ** pow_10) * 10 ** pow_10
    line_interval = abs(max_lines) / (5 if 1000 > max_lines > 0.01 else 10)

    longest_value_lines = max(len(str(max_lines)), len(str(line_interval)))

    common_options = get_common_echart_options()
    x_axis = common_options['xAxis'][0]
    del x_axis['data']
    x_axis['type'] = 'value'
    x_axis['scale'] = True
    common_options['yAxis'][0]['scale'] = True

    common_options.update({
        'xAxis': [{
            'data': '#set_data#',
            'fontFamily': 'Rubik',
            'axisPointer': {'type': 'shadow'},
            'type': 'category',
            'nameLocation': 'middle',
            'nameGap': 35,
        }],
        'yAxis': [
            {
                'type': 'value',
                'fontFamily': 'Rubik',
                'axisLabel': {
                    'formatter': '{value}'+bar_suffix
                },
                'nameLocation': 'middle',
                'nameGap': 24+7*(longest_value_bars+int(len(bar_suffix))),
                'alignTicks': True,
                'axisLine': {
                    'show': True,
                    'lineStyle': {
                        'color': ShimokuPalette.CHART_C1.value
                    }
                },
                'splitNumber': 5,
                'interval': bar_interval,
                'max': max_bars,
            },
            {
                'type': 'value',
                'fontFamily': 'Rubik',
                'axisLabel': {
                    'formatter': '{value}'+line_suffix
                },
                'nameLocation': 'middle',
                'nameGap': 24+7*(longest_value_lines+int(len(line_suffix))),
                'axisLine': {
                    'show': True,
                    'lineStyle': {
                        'color': f'var(--chart-C{len(bar_names)+2})'
                    }
                },
                'splitNumber': 5,
                'interval': line_interval,
                'max': max_lines,
            }
        ],
    })
    series_options = get_common_series_options()

    series = []
    for index, name in enumerate(bar_names):
        sop = deepcopy(series_options)
        sop.update({
            'name': name,
            'type': 'bar',
            'itemStyle': {
                'color': f'var(--chart-C{index+1})',
                'borderRadius': [9, 9, 0, 0]
            },
            'emphasis':
                {
                    'itemStyle': {
                        'color': f'var(--chart-C{index+1})',
                        'borderRadius': [9, 9, 0, 0]
                    },
                    'lineStyle': {
                        'color': f'var(--chart-C{index+1})',
                    }
                },
            'smooth': True,
        })
        series.append(sop)

    for index, name in enumerate(line_names):
        sop = deepcopy(series_options)
        sop.update({
            'name': name,
            'type': 'line',
            'yAxisIndex': 1,
            'itemStyle': {
                'color': f'var(--chart-C{len(bar_names) + index + 1})',
                'borderRadius': [9, 9, 0, 0]
            },
            'emphasis':
                {
                    'itemStyle': {
                        'color': f'var(--chart-C{len(bar_names) + index + 1})',
                        'borderRadius': [9, 9, 0, 0]
                    },
                    'lineStyle': {
                        'color': f'var(--chart-C{len(bar_names) + index + 1})',
                    }
                },
            'smooth': True,
        })
        series.append(sop)

    await self._create_trend_chart(
        echart_options=common_options, series_options=series,
        axes=x, values=bar_names+line_names, option_modifications=option_modifications,
        data_mapping_to_tuples=data_mappings_to_tuples,
        order=order, x_axis_names=x_axis_name,
        y_axis_names=[bar_axis_name, line_axis_name], variant=variant,
        title=title, rows_size=rows_size, cols_size=cols_size, padding=padding,
    )
