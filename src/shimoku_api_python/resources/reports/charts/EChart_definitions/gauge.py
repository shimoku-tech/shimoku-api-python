from typing import Optional, Dict, List, TYPE_CHECKING

import pandas as pd

from ..echart import get_common_echart_options, get_common_series_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def speed_gauge_chart(
    self: 'PlotApi', order: int, name: str, value: int,
    min_value: int, max_value: int, title: Optional[str] = None, rows_size: Optional[int] = 2,
    cols_size: Optional[int] = 3, padding: Optional[List[int]] = None,
    option_modifications: Optional[Dict] = None,
):
    """ Create a speed gauge chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    del common_options['yAxis']
    del common_options['xAxis']
    del common_options['grid']
    del common_options['toolbox']['feature']['magicType']
    common_options['grid'] = {'top': '1%', 'left': '1%', 'right': '1%'}
    common_options['tooltip']['trigger'] = 'item'
    series_options.update({
        'type': 'gauge',
        'min': min_value,
        'max': max_value,
        'progress': {'show': True, 'width': 18},
        'axisLine': {'lineStyle': {'width': 18}},
        'axisTick': {'show': False},
        'splitLine': {'length': 15, 'lineStyle': {'width': 2, 'color': '#999'}},
        'axisLabel': {'distance': 25, 'color': '#999', 'fontSize': 10},
        'anchor': {'show': True, 'showAbove': True, 'size': 25, 'itemStyle': {'borderWidth': 10}},
        'title': {'show': True, 'offsetCenter': [0, '45%'], 'fontSize': 20},
        'detail': {'valueAnimation': True, 'fontSize': 20, 'offsetCenter': [0, '70%']},
    })
    common_options['series'] = [series_options]

    await self._create_echart(
        fields=[{'name': 'name', 'value': 'value'}], options=common_options, option_modifications=option_modifications,
        data_mapping_to_tuples=await self._choose_data(order, pd.DataFrame([{'name': name, 'value': value}])),
        order=order, title=title, rows_size=rows_size, cols_size=cols_size, padding=padding)
