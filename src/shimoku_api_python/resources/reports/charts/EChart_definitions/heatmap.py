from typing import Optional, Dict, List, Tuple, Union, TYPE_CHECKING

import pandas as pd

from ..echart import get_common_echart_options, get_common_series_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

from shimoku_api_python.exceptions import DataError

import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def heatmap_chart(
    self: 'PlotApi', order: int, x: str, y: str, values: str,
    data: Union[List[Dict], pd.DataFrame, str], color_range: Optional[Tuple[int, int]] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    title: Optional[str] = None, padding: Optional[List[int]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    calculate_color_range: Optional[bool] = False, continuous: Optional[bool] = False,
    option_modifications: Optional[Dict] = None, variant: Optional[str] = None
):
    """ Create a heatmap chart """
    color_range = (0, 10) if color_range is None else color_range
    if calculate_color_range:
        aux_data = data
        if isinstance(aux_data, str):
            if aux_data not in self._shared_data:
                log_error(
                    logger,
                    f"Shared data set ({aux_data}) not found in the menu path ({str(self._app)})",
                    DataError
                )
            aux_data = self._shared_data[aux_data]
        if isinstance(aux_data, pd.DataFrame):
            aux_data = aux_data.to_dict('records')
        color_range = (min([row[values] for row in aux_data]), max([row[values] for row in aux_data]))
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    del common_options['legend']
    del common_options['toolbox']['feature']['magicType']
    common_options['xAxis'][0].update({'type': 'category', 'data': None})
    common_options['yAxis'][0].update({'type': 'category', 'nameGap': 64})
    common_options['visualMap'] = {'calculable': True, 'orient': 'vertical',
                                   'type': 'continuous' if continuous else 'piecewise',
                                   'left': 'right', 'top': 'center', 'show': variant != 'minimal',
                                   'min': color_range[0], 'max': color_range[1]}
    common_options['grid'].update({'top': '5%', 'right': 80, 'bottom': 28, 'left': '5%' if y_axis_name else '1%'})

    series_options.update({
        'type': 'heatmap',
        'itemStyle': {'borderRadius': [0, 0, 0, 0]},
    })
    await self._create_trend_chart(
        data_mapping_to_tuples=await self._choose_data(order, data), axes=[], values=[(x, y, values)],
        echart_options=common_options, series_options=series_options, order=order, title=title, padding=padding,
        rows_size=rows_size, cols_size=cols_size, show_values='all', x_axis_names=x_axis_name, y_axis_names=y_axis_name,
        option_modifications=option_modifications, variant=variant
    )
