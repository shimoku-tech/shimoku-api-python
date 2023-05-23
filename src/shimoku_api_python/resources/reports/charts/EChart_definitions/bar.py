from typing import TYPE_CHECKING

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
async def bar_chart(self: 'PlotApi', *args, x: str, **kwargs):
    """ Create a bar chart """
    series_options = get_common_series_options()
    series_options['type'] = 'bar'
    await self._create_trend_chart(
        *args, echart_options=get_common_echart_options(), axes=x, values=kwargs.pop('y', None),
        series_options=series_options,
        data_mapping_to_tuples=await self._choose_data(kwargs['order'], data=kwargs.get('data')), **kwargs)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def stacked_bar_chart(self: 'PlotApi', *args, x: str, **kwargs):
    """ Create a stacked bar chart """
    series_options = get_common_series_options()
    series_options.update({
        'type': 'bar',
        'areaStyle': {},
        'stack': 'stack',
        'itemStyle': {'borderRadius': [0, 0, 0, 0]},
    })
    data_mapping_to_tuples = await self._choose_data(kwargs['order'], data=kwargs.get('data'))
    y = kwargs.pop('y', None)
    len_y = len(y) if y else len(data_mapping_to_tuples.keys())-1
    series_options = [series_options] * (len_y-1)
    series_options.append(deepcopy(series_options[-1]))
    series_options[-1]['itemStyle']['borderRadius'] = [9, 9, 0, 0]
    await self._create_trend_chart(
        *args, echart_options=get_common_echart_options(), axes=x, values=y, series_options=series_options,
        data_mapping_to_tuples=data_mapping_to_tuples, **kwargs)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def zero_centered_bar_chart(self: 'PlotApi', *args, x: str, **kwargs):
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
        *args, echart_options=common_options, axes=x, values=kwargs.pop('y', None),
        series_options=series_options,
        data_mapping_to_tuples=await self._choose_data(kwargs['order'], data=kwargs.get('data')), **kwargs)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def horizontal_bar_chart(self: 'PlotApi', *args, x: str, **kwargs):
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
        *args, echart_options=common_options, axes=x, values=kwargs.pop('y', None),
        series_options=series_options,
        data_mapping_to_tuples=await self._choose_data(kwargs['order'], data=kwargs.get('data')), **kwargs)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def stacked_horizontal_bar_chart(self: 'PlotApi', *args, x: str, **kwargs):
    """ Create a stacked horizontal bar chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options.update({
        'type': 'bar',
        'areaStyle': {},
        'stack': 'stack',
        'itemStyle': {'borderRadius': [0, 0, 0, 0]},
    })
    data_mapping_to_tuples = await self._choose_data(kwargs['order'], data=kwargs.get('data'))
    y = kwargs.pop('y', None)
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
        *args, echart_options=common_options, axes=x, values=y, series_options=series_options,
        data_mapping_to_tuples=data_mapping_to_tuples, **kwargs)


