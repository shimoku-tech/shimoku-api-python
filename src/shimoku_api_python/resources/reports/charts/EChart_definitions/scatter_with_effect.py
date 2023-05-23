from typing import Optional, Dict,  Union, List, TYPE_CHECKING

from pandas import DataFrame

from ..echart import get_common_echart_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager
from shimoku_api_python.utils import validate_data_is_pandarable

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def scatter_with_effect_chart(
        self: 'PlotApi', order: int, x: str = 'x', y: str = 'y',
        data: Optional[Union[List[str], DataFrame, List[Dict]]] = None,
        x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
        title: Optional[str] = None, rows_size: Optional[int] = None, cols_size: Optional[int] = None,
        padding: Optional[List[int]] = None, effect_points: Optional[List] = None,
        option_modifications: Optional[Dict] = None,
):
    """ Create a scatter chart """
    data_mappings_to_tuples = await self._choose_data(order, data)
    if isinstance(data, str):
        data = self._shared_data[data]

    df: DataFrame = validate_data_is_pandarable(data)
    df = df[[x, y]].dropna()
    matrix = df.values

    common_options = get_common_echart_options()
    x_axis = common_options['xAxis'][0]
    del x_axis['data']
    x_axis['type'] = 'value'
    x_axis['scale'] = True
    common_options['yAxis'][0]['scale'] = True
    del common_options['toolbox']['feature']['magicType']
    common_options['series'] = [
        {
            'data': [(point if isinstance(point, list) else list(matrix[point]))
                     for point in effect_points],
            'type': 'effectScatter',
            'symbolSize': 20,
        },
        {
            'type': 'scatter',
            'itemStyle': {
                'color': 'var(--chart-C2)',
            },
            'data': '#set_data#'
        }
    ]

    await self._create_echart(
        options=common_options, fields=[(x, y)], data_mapping_to_tuples=data_mappings_to_tuples,
        order=order, x_axis_names=x_axis_name, y_axis_names=y_axis_name, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding, option_modifications=option_modifications
    )
