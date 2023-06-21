from typing import Optional, Dict,  Union, List, TYPE_CHECKING

from ..echart import get_common_echart_options, get_common_series_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def treemap_chart(
    self: 'PlotApi', order: int, data: Optional[Union[Dict, List]] = None,
    title: Optional[str] = None, padding: Optional[List[int]] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    option_modifications: Optional[Dict] = None,
):
    """ Create a treemap chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    del common_options['xAxis']
    del common_options['yAxis']
    del common_options['toolbox']['feature']['magicType']
    if isinstance(data, dict):
        data = [data]
    series_options.update({
        'type': 'treemap',
        'data': '#set_data#',
        'itemStyle': {'borderRadius': 0, 'gapWidth': 1},
    })
    common_options.update({
        'tooltip': {
            'trigger': 'item',
            'triggerOn': 'mousemove'
        },
        'series': series_options
    })
    await self._create_echart(
        data_mapping_to_tuples=await self._choose_data(order, data, dump_whole=True),
        fields=['data'], options=common_options, order=order, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding,
        option_modifications=option_modifications
    )
