from typing import Optional,  Union, TYPE_CHECKING

if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi
from shimoku_api_python.exceptions import BentoboxError
from shimoku_api_python.utils import interpret_color, ShimokuPalette

import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


@logging_before_and_after(logging_level=logger.info)
def gauge_indicator(
    self: 'PlotApi', order: int, value: int,
    title: Optional[str] = "", description: Optional[str] = "",
    cols_size: Optional[int] = 6, rows_size: Optional[int] = 1,
    color: Union[str, int] = 1,
):
    bentobox_data = {
        'bentoboxId': f'_{order}',
        'bentoboxOrder': order,
        'bentoboxSizeColumns': cols_size,
        'bentoboxSizeRows': rows_size,
    }

    if self._bentobox_data:
        log_error(logger, 'The gauges group uses a bentobox, so it cannot be used inside another bentobox. Please'
                          ' pop out of the current bentobox before using this function.', BentoboxError)
    self._bentobox_data = bentobox_data

    indicator_data = [
        {
            'description': description,
            'title': title,
            'value': '',
            'color': '',
            'align': 'left'
        }
    ]

    self.indicator(data=indicator_data, order=order, rows_size=8, cols_size=15, padding='1, 1, 0, 1',
                   logging_func_name='gi_indicator')

    color = interpret_color(color)

    options = {
        'grid': {
            'left': ['5%'],
            'right': ['5%'],
            'top': ['5%'],
            'bottom': ['5%'],
            'containLabel': True
        },
        'series': [
            {
                'data': '#set_data#',
                'type': 'gauge',
                'startAngle': 360,
                'endAngle': 0,
                'radius': '80%',
                'center': ['50%', '40%'],
                'min': 0,
                'max': 100,
                'pointer': {
                    'show': False,
                },
                'progress': {
                    'show': True,
                    'width': 20,
                    'overlap': False,
                    'roundCap': False,
                    'clip': False,
                    'itemStyle': {
                        'borderWidth': 0,
                        'color': color,
                    }
                },
                'splitLine': {
                    'show': False,
                },
                'axisLine': {'lineStyle': {'width': 20}},
                'axisTick': {
                    'show': False
                },
                'axisLabel': {
                    'show': False,
                },
                'title': {
                    'show': False,
                    'fontSize': 16,
                    'fontFamily': 'Rubik',
                },
                'detail': {
                    'fontSize': 24,
                    'fontFamily': 'Rubik',
                    'font': 'inherit',
                    'color': ShimokuPalette.BLACK.value,
                    'borderColor': 'auto',
                    'borderWidth': 0,
                    'formatter': '{value}%',
                    'valueAnimation': True,
                    'offsetCenter': ['0', '60']
                }
            }
        ]
    }

    self.free_echarts(
        data=[{'value': value}],
        fields=[{'value': 'value'}],
        options=options,
        order=order + 1, rows_size=6, cols_size=7,
        padding='1, 0, 1, 0',
        logging_func_name='gi_gauge'
    )
    self._bentobox_data = {}


