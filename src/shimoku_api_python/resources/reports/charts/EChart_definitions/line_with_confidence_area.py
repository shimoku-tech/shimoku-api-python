from typing import Optional, Union, List, TYPE_CHECKING, Dict

from ..echart import get_common_echart_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

from pandas import DataFrame

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def line_with_confidence_area_chart(
    self: 'PlotApi',
    data: Union[str, DataFrame, List[Dict]], order: Optional[int] = None,
    x: str = 'x', lower: str = 'l', y: str = 'y', upper: str = 'u',
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[str] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    percentages: bool = False, option_modifications: Optional[Dict] = None,
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
                'color': 'var(--chart-C1)'
            },
            'emphasis': {
                'lineStyle': {
                    'color': 'var(--chart-C1)'
                }
            },
            'showSymbol': False
        }
    ]

    await self._create_trend_chart(
        data_mapping_to_tuples=await self._choose_data(order, data), order=order, axes=x, values=[lower, upper, y],
        rows_size=rows_size, cols_size=cols_size, padding=padding, title=title, x_axis_names=x_axis_name,
        y_axis_names=y_axis_name, echart_options=common_options, series_options=series_options,
        option_modifications=option_modifications
    )
