from typing import Optional, Dict,  Union, List, TYPE_CHECKING
from pandas import DataFrame

from ..echart import get_common_echart_options, get_common_series_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def segmented_line_chart(
    self: 'PlotApi', order: int, x: str = 'x', y: Union[str, List[str]] = 'y',
    data: Optional[Union[str, DataFrame, List[Dict]]] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None, title: Optional[str] = None,
    marking_lines: Optional[List[int]] = None,
    range_colors: Optional[List[str]] = None,
    option_modifications: Optional[Dict] = None,
):
    """ Create a chart with bars and lines. """
    data_mappings_to_tuples = await self._choose_data(order, data)

    if isinstance(y, str):
        y = [y]

    if not marking_lines:
        marking_lines = [0]

    common_options = get_common_echart_options()
    common_options['xAxis'][0]['boundaryGap'] = False
    common_options['grid']['right'] = '8%'
    common_options.update({
        'visualMap': {
            'top': 50,
            'right': 10,
            'itemSymbol': 'circle',
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
        'color': 'var(--chart-C5)',
        'markLine': {
            'data': [{'yAxis': val} for val in marking_lines],
            'itemStyle': {
                'color': 'var(--chart-C5)',
                'opacity': 0.5
            },
        }
    })

    await self._create_trend_chart(
        data_mapping_to_tuples=data_mappings_to_tuples, axes=x, values=y,
        echart_options=common_options, series_options=series_options,
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name,
        title=title, rows_size=rows_size, cols_size=cols_size, padding=padding,
        option_modifications=option_modifications
    )
