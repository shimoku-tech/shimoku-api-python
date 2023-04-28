from typing import Optional, Union, List, TYPE_CHECKING

from copy import deepcopy

from ..echart import get_common_echart_options, get_common_series_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import NewPlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def line_chart(self: 'NewPlotApi', *args, x: str, **kwargs):
    """ Create a line chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options['type'] = 'line'
    common_options['yAxis'][0]['scale'] = True
    await self._create_trend_chart(
        *args, echart_options=get_common_echart_options(), axes=x, values=kwargs.pop('y', None),
        series_options=series_options, data_mapping_to_tuples=await self._choose_data(kwargs.get('data')), **kwargs)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def area_chart(self: 'NewPlotApi', *args, x: str, **kwargs):
    """ Create an area chart """
    series_options = get_common_series_options()
    series_options.update({
        'type': 'line',
        'areaStyle': {'opacity': 0.5},
    })
    await self._create_trend_chart(
        *args, echart_options=get_common_echart_options(), axes=x, values=kwargs.pop('y', None),
        series_options=series_options, data_mapping_to_tuples=await self._choose_data(kwargs.get('data')), **kwargs)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def stacked_area_chart(self: 'NewPlotApi', *args,  x: str, **kwargs):
    """ Create a stacked area chart """
    series_options = get_common_series_options()
    series_options.update({
        'type': 'line',
        'areaStyle': {},
        'stack': 'stack',
        'itemStyle': {'borderRadius': [0, 0, 0, 0]},
    })
    data_mapping_to_tuples = await self._choose_data(kwargs.get('data'))
    y = kwargs.pop('y', None)
    len_y = len(y) if y else len(data_mapping_to_tuples.keys())-1
    series_options = [series_options] * (len_y-1)
    series_options.append(deepcopy(series_options[-1]))
    series_options[-1]['itemStyle']['borderRadius'] = [9, 9, 0, 0]
    await self._create_trend_chart(
        *args, echart_options=get_common_echart_options(), axes=x, values=y, series_options=series_options,
        data_mapping_to_tuples=data_mapping_to_tuples, bottom_toolbox=False, **kwargs)
