from typing import Optional, Dict,  Union, List, TYPE_CHECKING

from pandas import DataFrame

from ..echart import get_common_echart_options, get_common_series_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager
from shimoku_api_python.utils import calculate_percentages_from_list
from shimoku_api_python.exceptions import BentoboxError
from shimoku_api_python.utils import interpret_color

import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def shimoku_gauge_chart(
    self: 'PlotApi', order: int,
    value: Union[int, float], name: str = "",
    color: Optional[Union[str, int]] = 1, title: Optional[str] = None,
    rows_size: Optional[int] = 1, cols_size: Optional[int] = 3,
    padding: Optional[List[int]] = None,
    is_percentage: bool = False,
    option_modifications: Optional[Dict] = None,
):
    """ Create a pie chart """

    color = interpret_color(color)

    value_font_size = 24 * max(min(rows_size, int(cols_size / 2)), 1)

    if self._bentobox_data:
        value_font_size = 35 * max(int(min(rows_size / 10,
                                   (cols_size - self._bentobox_data['bentoboxSizeColumns']) / 4)), 1)

    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    del common_options['yAxis']
    del common_options['xAxis']
    del common_options['grid']
    del common_options['toolbox']
    common_options['tooltip']['trigger'] = 'item'
    common_options['grid'] = {
        'left': '5%',
        'right': '5%',
        'top': '5%',
        'bottom': '5%',
        'containLabel': True
    }
    series_options.update({
        'type': 'gauge',
        'startAngle': 180,
        'endAngle': 0,
        'radius': '100%',
        'min': 0,
        'max': 100,
        'pointer': {
            'show': False,
        },
        'progress': {
            'show': True,
            'width': 30 if rows_size > 1 else 25,
            'overlap': False,
            'roundCap': False,
            'clip': False,
            'itemStyle': {
                'borderWidth': 0,
                'borderColor': color,
                'color': color,
            }
        },
        'splitLine': {
            'show': False,
        },
        'axisLine':
            {'lineStyle':
                 {'width': 30 if rows_size > 1 else 25}
             },
        'axisTick': {
            'show': False
        },
        'axisLabel': {
            'show': False,
        },
        'title': {
            'fontSize': 16,
            'fontFamily': 'Rubik',
            'offsetCenter': ['0', '30'],
        },
        'detail': {
            'fontSize': value_font_size,
            'fontFamily': 'Rubik',
            'font': 'inherit',
            'color': '#202A36',
            'borderColor': 'auto',
            'borderWidth': 0,
            'formatter': ('-' if value < 0 else '') + '{value}' + ('%' if is_percentage else ''),
            'valueAnimation': True,
            'offsetCenter': ['0', '-10']
        }
    })
    common_options['series'] = [series_options]

    await self._create_echart(
        fields=[{'name': 'name', 'value': 'value'}], options=common_options, option_modifications=option_modifications,
        data_mapping_to_tuples=await self._choose_data(order, DataFrame([{'name': name, 'value': abs(value)}])),
        order=order, title=title, rows_size=rows_size, cols_size=cols_size, padding=padding)


@logging_before_and_after(logger.info)
def shimoku_gauges_group(
        self: 'PlotApi', gauges_data: Union[DataFrame, List[Dict]], order: int,
        rows_size: Optional[int] = None, cols_size: Optional[int] = 12,
        gauges_padding: Optional[str] = '3, 1, 1, 1',
        gauges_rows_size: Optional[int] = 9, gauges_cols_size: Optional[int] = 4,
        calculate_percentages: Optional[bool] = False
):
    if isinstance(gauges_data, DataFrame):
        gauges_data = gauges_data.to_dict(orient="records")

    if calculate_percentages:
        percentages = calculate_percentages_from_list([gauge['value'] for gauge in gauges_data], 0)
        for i in range(len(percentages)):
            gauges_data[i]['value'] = percentages[i]

    if self._bentobox_data:
        log_error(logger, 'The gauges group uses a bentobox, so it cannot be used inside another bentobox. Please'
                          ' pop out of the current bentobox before using this function.', BentoboxError)
    self.set_bentobox(cols_size, rows_size)
    for gauge in gauges_data:
        order += 1
        self.shimoku_gauge(
            value=gauge['value'], order=order, name=gauge.get('name'),
            padding=gauge['padding'] if gauge.get('padding') else gauges_padding,
            color=gauge['color'] if gauge.get('color') else 1,
            rows_size=gauge['rows_size'] if gauge.get('rows_size') else gauges_rows_size,
            cols_size=gauge['cols_size'] if gauge.get('cols_size') else gauges_cols_size,
            is_percentage=gauge['is_percentage'] if gauge.get('is_percentage') else True,
        )
    self.pop_out_of_bentobox()
    return order + 1
