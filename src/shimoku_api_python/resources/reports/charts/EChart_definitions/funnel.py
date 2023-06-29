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
async def funnel_chart(
    self: 'PlotApi', order: int, names: str, values: str,
    data: Union[str, DataFrame, List[Dict]], title: Optional[str] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[List[int]] = None,
    option_modifications: Optional[Dict] = None
):
    """ Create a scatter chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    del common_options['xAxis']
    del common_options['yAxis']
    del common_options['toolbox']['feature']['magicType']
    common_options['legend']['data'] = '#set_data#'
    common_options['tooltip'] = {
        'trigger': 'item',
        'formatter': "{a} <br/>{b} : {c}%"
    }
    series_options.update({
        'type': 'funnel',
        'left': '10%',
        'top': "10%",
        'bottom': '10%',
        'width': '80%',
        'min': 0,
        'max': 100,
        'minSize': '0%',
        'maxSize': '100%',
        'sort': 'descending',
        'gap': 2,
        'label': {
            'show': True,
            'position': 'inside'
        },
        'labelLine': {
            'length': 10,
            'lineStyle': {
                'width': 1,
                'type': 'solid'
            }
        },
        'itemStyle': {
            'borderColor': '#fff',
            'borderWidth': 1
        },
        'emphasis': {
            'label': {
                'fontSize': 20
            }
        }
    })
    common_options.update({
        'series': series_options
    })

    await self._create_echart(
        fields=[names, {'name': names, 'value': values}], options=common_options,
        data_mapping_to_tuples=await self._choose_data(order, data), option_modifications=option_modifications,
        order=order, title=title, rows_size=rows_size, cols_size=cols_size, padding=padding)
