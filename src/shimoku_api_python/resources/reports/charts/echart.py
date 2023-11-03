from ...report import Report
from copy import deepcopy
from typing import Dict, Any

from shimoku_api_python.utils import ShimokuPalette


class EChart(Report):
    """ ECharts report class """
    report_type = 'ECHARTS2'

    default_properties = dict(
        hash=None,
        option={},
    )


default_toolbox_options = {
    'show': True,
    'orient': 'horizontal',
    'itemSize': 20,
    'itemGap': 24,
    'showTitle': True,
    'zlevel': 100,
    'bottom': 0,
    'right': '24px',
    'feature': {
        'dataView': {
            'title': 'data',
            'readOnly': False,
            'icon': 'image://https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/6398a555461a3684b16d544e_database.svg',
            'emphasis': {
                'iconStyle': {
                    'textBackgroundColor': ShimokuPalette.CHART_C1.value,
                    'textBorderRadius': [50, 50, 50, 50],
                    'textPadding': [8, 8, 8, 8],
                    'textFill': ShimokuPalette.WHITE.value
                }
            },
        },
        'magicType': {
            'type': ['line', 'bar'],
            'title': {
                'line': 'Switch to Line Chart',
                'bar': 'Switch to Bar Chart',
            },
            'icon': {
                'line': 'image://https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/6398a55564d52c1ba4d9884d_linechart.svg',
                'bar': 'image://https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/6398a5553cc6580f8e0edea4_barchart.svg'
            },
            'emphasis': {
                'iconStyle': {
                    'textBackgroundColor': ShimokuPalette.CHART_C1.value,
                    'textBorderRadius': [50, 50, 50, 50],
                    'textPadding': [8, 8, 8, 8],
                    'textFill': ShimokuPalette.WHITE.value
                }
            },
        },
        'saveAsImage': {
            'show': True,
            'title': 'Save as image',
            'icon': 'image://https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/6398a555662e1af339154c64_download.svg',
            'emphasis': {
                'iconStyle': {
                    'textBackgroundColor': ShimokuPalette.CHART_C1.value,
                    'textBorderRadius': [50, 50, 50, 50],
                    'textPadding': [8, 8, 8, 8],
                    'textFill': ShimokuPalette.WHITE.value
                }
            }
        }
    }
}


def get_common_echart_options() -> Dict[str, Any]:
    # toolbox_options = deepcopy(default_toolbox_options)
    # if bottom_toolbox:
    #     del toolbox_options['top']
    #     toolbox_options['bottom'] = "0px"
    return deepcopy({
        'legend': {
            'show': True,
            'type': 'scroll',
            'icon': 'circle',
            'padding': [5, 5, 5, 5],
        },
        'tooltip': {
            'trigger': 'item',
            'axisPointer': {'type': 'cross'},
        },
        'toolbox': default_toolbox_options,
        'xAxis': [{
            'data': '#set_data#',
            'type': 'category',
            'fontFamily': 'Rubik',
            'name': "",
            'nameLocation': 'middle',
        }],
        'yAxis': [{
            'name': "",
            'nameLocation': 'middle',
            'type': 'value',
            'fontFamily': 'Rubik',
        }],
        'grid': {
            'left': '1%',
            'right': '2%',
            'bottom': 48,
            'containLabel': True
        },
    })


def get_common_series_options() -> Dict[str, Any]:
    return deepcopy({
        'data': '#set_data#',
        'emphasis': {'focus': 'series'},
        'smooth': True,
        'itemStyle': {'borderRadius': [9, 9, 0, 0]},
    })
