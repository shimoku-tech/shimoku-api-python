from typing import Optional, Dict,  Union, List, Tuple, TYPE_CHECKING

from pandas import DataFrame

from ..echart import get_common_echart_options, get_common_series_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import NewPlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def tree_chart(self: 'NewPlotApi', order: int, data: Optional[Dict] = None,
                     radial: bool = False, vertical: bool = False,
                     title: Optional[str] = None, padding: Optional[List[int]] = None,
                     rows_size: Optional[int] = None, cols_size: Optional[int] = None,
                     ):
    """ Create a tree chart """
    if radial and vertical:
        logger.warning('Radial and vertical options are mutually exclusive. Vertical option will be ignored.')
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    del common_options['xAxis']
    del common_options['yAxis']
    del common_options['toolbox']['feature']['magicType']
    series_options.update({
        'type': 'tree',
        'data': None,
        'symbolSize': 7,
        'initialTreeDepth': 3,
        'layout': 'orthogonal' if not radial else 'radial',
        'orient': 'horizontal' if not vertical else 'vertical',
        'label': {
            'position': 'left' if not vertical else 'top',
            'rotate': 0 if not vertical else -90,
            'verticalAlign': 'middle',
            'align': 'right',
            'fontSize': 9
        },
        'leaves': {
            'label': {
                'position': 'right' if not vertical else 'bottom',
                'rotate': 0 if not vertical else -90,
                'verticalAlign': 'middle',
                'align': 'left' if not vertical else 'right'
            }
        },
        'emphasis': {
            'focus': 'descendant'
        },
        'expandAndCollapse': True,
        'animationDuration': 550,
        'animationDurationUpdate': 750
    })
    common_options.update({
        'tooltip': {
            'trigger': 'item',
            'triggerOn': 'mousemove'
        },
        'series': series_options
    })
    if radial:
        del common_options['series']['orient']
        del common_options['series']['leaves']
        del common_options['series']['label']

    await self._create_echart(
        data_mapping_to_tuples=await self._choose_data(data),
        fields=['data'], options=common_options, order=order, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding)
