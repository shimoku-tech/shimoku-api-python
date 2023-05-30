from ...report import Report
from copy import deepcopy
from typing import Optional, Dict, Any


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
    'top': "0px",
    'right': "24px",
    'feature': {
        'dataView': {
            'title': 'Data',
            'readOnly': False,
            'icon': 'image://https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/6398a555461a3684b16d544e_database.svg',
            'emphasis': {
                'iconStyle': {
                    'textBackgroundColor': 'var(--chart-C1)',
                    'textBorderRadius': [50, 50, 50, 50],
                    'textPadding': [8, 8, 8, 8],
                    'textFill': 'var(--color-white)'
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
                    'textBackgroundColor': 'var(--chart-C1)',
                    'textBorderRadius': [50, 50, 50, 50],
                    'textPadding': [8, 8, 8, 8],
                    'textFill': 'var(--color-white)'
                }
            },
        },
        'saveAsImage': {
            'show': True,
            'title': 'Save as image',
            'icon': 'image://https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/6398a555662e1af339154c64_download.svg',
            'emphasis': {
                'iconStyle': {
                    'textBackgroundColor': 'var(--chart-C1)',
                    'textBorderRadius': [50, 50, 50, 50],
                    'textPadding': [8, 8, 8, 8],
                    'textFill': 'var(--color-white)'
                }
            }
        }
    }
}


def get_common_echart_options() -> Dict[str, Any]:
    return deepcopy({
        'legend': {
            'show': True,
            'type': 'scroll',
            'icon': 'circle',
            'padding': [5, 400, 5, 5],
        },
        'tooltip': {
            'trigger': 'item',
            'axisPointer': {'type': 'cross'},
        },
        'toolbox': default_toolbox_options,
        'xAxis': [{
            'data': None,
            'type': 'category',
            'fontFamily': 'Rubik',
            'name': "",
            'nameLocation': 'middle',
            'boundaryGap': True,
            'nameGap': 35,
        }],
        'yAxis': [{
            'name': "",
            'nameLocation': 'middle',
            'nameGap': 35,
            'boundaryGap': True,
            'type': 'value',
            'fontFamily': 'Rubik',
        }],
        'dataZoom': [{'show': True}, {'type': 'inside'}],
        'grid': {
            'left': '32px',
            'right': '32px',
            'bottom': '55px',
            'containLabel': True
        },
    })


def get_common_series_options() -> Dict[str, Any]:
    return deepcopy({
        'data': None,
        'emphasis': {'focus': 'series'},
        'smooth': True,
        'itemStyle': {'borderRadius': [9, 9, 0, 0]},
    })
