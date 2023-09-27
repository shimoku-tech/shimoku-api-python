from typing import Optional, Dict,  Union, List, TYPE_CHECKING

from pandas import DataFrame

from ..echart import (get_common_echart_options, get_common_series_options,
                      InvertibleDictFunction, generic_echart_function_params)
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager
from shimoku_api_python.utils import get_arg_names

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)

common_opt = get_common_echart_options()


def get_pie_chart_options_function() -> InvertibleDictFunction:
    pie_func = InvertibleDictFunction(pie_chart)
    pie_func.set_items(get_common_echart_options())
    pie_func.delete_items(['yAxis', 'xAxis', 'grid'])
    pie_func.delete_items(offset=['toolbox', 'feature'], keys=['magicType'])
    pie_func.set_items(
        final=True, offset=['series', 0],
        items={
            'type': 'pie',
            'data': '#set_data#',
            'itemStyle': {
                'borderWidth': 0,
                'borderRadius': 5
            },
            'radius': '70%'
        },
    )
    pie_func.custom_operation(
        func=lambda params:
            params.update(
                {'fields': [{'name': pie_func.params['names'], 'value': pie_func.params['values']}]}
            ),
        inverse_func=lambda params:
            (params.update({
                'names': pie_func.params['fields'][0]['name'],
                'values': pie_func.params['fields'][0]['value']}
            ), params.pop('fields'))
    )
    pie_func.params_to_params(generic_echart_function_params, replace=True)
    return pie_func


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def pie_chart(
    self: 'PlotApi', order: int, names: str, values: str,
    data: Union[str, DataFrame, List[Dict]],
    title: Optional[str] = None, rows_size: Optional[int] = 2,
    cols_size: Optional[int] = 3, padding: Optional[List[int]] = None,
    option_modifications: Optional[Dict] = None,
):
    """ Create a pie chart """
    local_vars = locals()
    kwargs = {k: local_vars[k] for k in get_arg_names(pie_chart) if k != 'self' and k in local_vars}
    pie_func = get_pie_chart_options_function()
    await self._create_echart(**pie_func(**kwargs))


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def doughnut_chart(
    self: 'PlotApi', order: int, names: str, values: str,
    data: Union[str, DataFrame, List[Dict]],
    title: Optional[str] = None, rows_size: Optional[int] = 2,
    cols_size: Optional[int] = 3, padding: Optional[List[int]] = None,
    option_modifications: Optional[Dict] = None,
):
    """ Create a doughnut chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    del common_options['yAxis']
    del common_options['xAxis']
    del common_options['grid']
    del common_options['toolbox']['feature']['magicType']
    common_options['tooltip']['trigger'] = 'item'
    series_options.update({
        'type': 'pie',
        'data': '#set_data#',
        'itemStyle': {'borderWidth': 0, 'borderRadius': 5},
        'radius': ['40%', '70%'],
        'label': {'show': False, 'position': 'center'},
        'emphasis': {'label': {'show': True, 'fontSize': '30', 'fontWeight': 'bold'}},
        'labelLine': {'show': False}
    })
    common_options['series'] = [series_options]

    await self._create_echart(
        fields=[{'name': names, 'value': values}], options=common_options,
        data_mapping_to_tuples=await self._choose_data(order, data), option_modifications=option_modifications,
        order=order, title=title, rows_size=rows_size, cols_size=cols_size, padding=padding)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def rose_chart(
    self: 'PlotApi', order: int, names: str, values: str,
    data: Union[str, DataFrame, List[Dict]],
    title: Optional[str] = None, rows_size: Optional[int] = 2,
    cols_size: Optional[int] = 3, padding: Optional[List[int]] = None,
    option_modifications: Optional[Dict] = None,
):
    """ Create a rose chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    del common_options['yAxis']
    del common_options['xAxis']
    del common_options['grid']
    del common_options['toolbox']['feature']['magicType']
    common_options['tooltip']['trigger'] = 'item'
    series_options.update({
        'type': 'pie',
        'roseType': 'area',
        'data': '#set_data#',
        'itemStyle': {'borderWidth': 0, 'borderRadius': 5},
        'radius': ['10%', '70%'],
    })
    common_options['series'] = [series_options]

    await self._create_echart(
        fields=[{'name': names, 'value': values}], options=common_options,
        data_mapping_to_tuples=await self._choose_data(order, data), option_modifications=option_modifications,
        order=order, title=title, rows_size=rows_size, cols_size=cols_size, padding=padding,
    )
