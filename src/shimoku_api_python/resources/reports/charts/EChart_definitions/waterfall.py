from typing import Optional, Union, List, TYPE_CHECKING, Dict

from ..echart import get_common_echart_options
if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi

from shimoku_api_python.async_execution_pool import async_auto_call_manager
from shimoku_api_python.utils import validate_data_is_pandarable, ShimokuPalette
from shimoku_api_python.exceptions import DataError

from pandas import DataFrame

import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


@async_auto_call_manager()
@logging_before_and_after(logger.info)
async def waterfall_chart(
    self: 'PlotApi',
    data: Union[str, DataFrame, List[Dict]], order: int,
    x: str, positive: str, negative: str,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    padding: Optional[str] = None, title: Optional[str] = None,
    x_axis_name: Optional[str] = None, y_axis_name: Optional[str] = None,
    show_balance: bool = False, variant: Optional[str] = None,
    option_modifications: Optional[Dict] = None,
):
    if isinstance(data, str):
        log_error(logger, f'Waterfall cannot use shared data, please provide a DataFrame or a list of dicts', DataError)

    df: DataFrame = validate_data_is_pandarable(data)

    df['Base'] = (df[positive].cumsum() - df[negative].cumsum()).shift(1).fillna(0)
    df['Value'] = df[positive] - df[negative]
    df['Balance'] = df['Base'] + df['Value']
    df['VisibleNegBase'] = 0
    df['VisiblePosBase'] = 0

    df['Positive'] = df['Value'].apply(lambda x: x if x > 0 else 0)
    df['Negative'] = df['Value'].apply(lambda x: abs(x) if x < 0 else 0)

    def change_sign(row):
        if row['Base'] < 0:
            if row['Base'] + row['Positive'] > 0:
                row['VisiblePosBase'] = -(row['Positive'] - (row['Base'] + row['Positive']))
                row['Positive'] = row['Base'] + row['Positive']
                row['Base'] = 0
                return row
            else:
                row['Positive'] = -row['Positive']
                row['Negative'] = -row['Negative']
        else:
            if row['Base'] - row['Negative'] < 0:
                row['VisibleNegBase'] = row['Negative'] + (row['Base'] - row['Negative'])
                row['Negative'] = row['Base'] - row['Negative']
                row['Base'] = 0
                return row

        row['Base'] = row['Base'] - row['Positive'] if row['Base'] < 0 else row['Base'] - row['Negative']
        return row

    df = df.apply(change_sign, axis=1)
    df = df[[x, 'Balance', 'Base', 'VisibleNegBase', 'VisiblePosBase', 'Negative', 'Positive']].fillna(0)

    data_mappings_to_tuples = await self._choose_data(order, df)

    common_options = get_common_echart_options()
    del common_options['toolbox']['feature']['magicType']
    common_options.update({
        'legend': {
            'data': [positive, negative] + (['Balance'] if show_balance else []),
            'show': True,
            'type': 'scroll',
            'itemGap': 16,
            'icon': 'circle'
        },
        'xAxis': [
            {
                'data': '#set_data#',
                'type': 'category',
                'fontFamily': 'Rubik',
                'nameLocation': 'middle',
                'nameGap': 35,
            }
        ],
        'yAxis': [
            {
                'type': 'value',
                'fontFamily': 'Rubik',
                'nameLocation': 'middle',
                'nameGap': int(24+7*(df['Balance'].astype(str).apply(len).max())),
            },
        ],
    })
    series_options = [
        {
            'data': '#set_data#',
            'name': 'Balance',
            'step': 'end',
            'symbol': 'none',
            'type': 'line',
            'itemStyle': {
                'color': ShimokuPalette.CHART_C3.value if show_balance else 'transparent',
            },
            'emphasis': {
                'itemStyle': {
                    'color': ShimokuPalette.CHART_C3.value if show_balance else 'transparent',
                },
                'lineStyle': {
                    'color': ShimokuPalette.CHART_C3.value if show_balance else 'transparent',
                }
            },
            'zlevel': 0,
            'tooltip': {'show': show_balance},
        },
        {
            'data': '#set_data#',
            'name': 'Placeholder',
            'type': 'bar',
            'stack': 'Total',
            'itemStyle': {
                'borderColor': 'transparent',
                'color': 'transparent'
            },
            'emphasis': {
                'itemStyle': {
                    'borderColor': 'transparent',
                    'color': 'transparent'
                }
            },
            'tooltip': {'show': False},
        },
        {
            'data': '#set_data#',
            'name': 'Negative visible Base',
            'type': 'bar',
            'stack': 'Total',
            'silent': True,
            'itemStyle': {
                'color': ShimokuPalette.CHART_C6.value,
            },
            'emphasis': {
                'itemStyle': {
                    'color': ShimokuPalette.CHART_C6.value,
                },
            },
            'zlevel': 1,
            'tooltip': {'show': False},
        },
        {
            'data': '#set_data#',
            'name': 'Positive visible Base',
            'type': 'bar',
            'stack': 'Total',
            'silent': True,
            'itemStyle': {
                'color': ShimokuPalette.CHART_C2.value,
            },
            'emphasis': {
                'itemStyle': {
                    'color': ShimokuPalette.CHART_C2.value,
                },
            },
            'zlevel': 1,
            'tooltip': {'show': False},
        },
        {
            'data': '#set_data#',
            'name': negative,
            'type': 'bar',
            'stack': 'Total',
            'itemStyle': {
                'borderRadius': [0, 0, 9, 9],
                'color': ShimokuPalette.CHART_C6.value,
            },
            'emphasis': {
                'itemStyle': {
                    'borderRadius': [0, 0, 9, 9],
                    'color': ShimokuPalette.CHART_C6.value,
                },
            },
            'zlevel': 1,
        },
        {
            'data': '#set_data#',
            'name': positive,
            'type': 'bar',
            'stack': 'Total',
            'itemStyle': {
                'borderRadius': [9, 9, 0, 0],
                'color': ShimokuPalette.CHART_C2.value,
            },
            'emphasis': {
                'itemStyle': {
                    'borderRadius': [9, 9, 0, 0],
                    'color': ShimokuPalette.CHART_C2.value,
                },
            },
            'zlevel': 1,
        },
    ]

    await self._create_trend_chart(
        data_mapping_to_tuples=data_mappings_to_tuples, order=order, axes=x,
        values=['Balance', 'Base', 'VisibleNegBase', 'VisiblePosBase', 'Negative', 'Positive'],
        rows_size=rows_size, cols_size=cols_size, padding=padding, title=title, x_axis_names=x_axis_name,
        y_axis_names=y_axis_name, echart_options=common_options, series_options=series_options,
        option_modifications=option_modifications, variant=variant
    )
