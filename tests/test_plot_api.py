""""""
from os import getenv
from typing import Dict, List

import datetime as dt

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
app_id: str = getenv('APP_ID')
app_type_id: str = getenv('APP_TYPE_ID')
app_element: Dict[str, str] = dict(
    business_id=business_id,
    app_id=app_id,
)


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
)
s.plt.set_business(business_id=business_id)


data = [
    {'date': dt.date(2021, 1, 1), 'x': 5, 'y': 5},
    {'date': dt.date(2021, 1, 2), 'x': 6, 'y': 5},
    {'date': dt.date(2021, 1, 3), 'x': 4, 'y': 5},
    {'date': dt.date(2021, 1, 4), 'x': 7, 'y': 5},
    {'date': dt.date(2021, 1, 5), 'x': 3, 'y': 5},
]


def test_bar():
    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/bar-test',
        row=1, column=1,
    )

    assert r

    s.plt.delete(
        menu_path='test/bar-test',
        component_type='bar',
        row=1, column=1,
    )


def test_line():
    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/line-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/line-test',
        row=1, column=1,
        component_type='line',
    )


def test_stockline():
    s.plt.stockline(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/stockline-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/stockline-test',
        component_type='stockline',
        row=1, column=1,
    )


def test_scatter():
    r = s.plt.scatter(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/scatter-test',
        row=1, column=1,
    )

    assert r

    s.plt.delete(
        menu_path='test/line-test',
        row=1, column=1,
        component_type='scatter',
    )


# TODO WiP
def test_scatter_with_confidence_area():
    r = s.plt.scatter_with_confidence_area(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/scatter-confidence-test',
        row=1, column=1,
    )

    assert r

    s.plt.delete(
        menu_path='test/scatter-confidence-test',
        row=1, column=1,
        component_type='scatter_with_confidence_area',
    )


def test_bubble_chart():
    # s.plt.bubble_chart()
    raise NotImplementedError


def test_candlestick():
    data_: List[Dict] = [
        {
            "date": "2021-01-24",
            "open": 78,
            "close": 85,
            "highest": 94,
            "lowest": 6
        },
        {
            "date": "2021-01-25",
            "open": 17,
            "close": 13,
            "highest": 7,
            "lowest": 18
        },
        {
            "date": "2021-01-26",
            "open": 18,
            "close": 38,
            "highest": 33,
            "lowest": 39
        },
        {
            "date": "2021-01-27",
            "open": 9,
            "close": 27,
            "highest": 46,
            "lowest": 93
        },
        {
            "date": "2021-01-28",
            "open": 59,
            "close": 45,
            "highest": 90,
            "lowest": 75
        },
        {
            "date": "2021-01-29",
            "open": 45,
            "close": 18,
            "highest": 0,
            "lowest": 68
        },
        {
            "date": "2021-01-30",
            "open": 48,
            "close": 57,
            "highest": 13,
            "lowest": 6
        },
        {
            "date": "2021-01-31",
            "open": 79,
            "close": 84,
            "highest": 58,
            "lowest": 14
        }
    ]
    s.plt.candlestick(
        data=data_, x='date',
        menu_path='test/candlestick-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/candlestick-test',
        component_type='candlestick',
        row=1, column=1,
    )


def test_funnel():
    data_ = [
        {
            "value": 60,
            "name": "Third"
        },
        {
            "value": 40,
            "name": "Fourth"
        },
        {
            "value": 20,
            "name": "Fifth"
        },
        {
            "value": 80,
            "name": "Second"
        },
        {
            "value": 100,
            "name": "First"
        }
    ]
    s.plt.funnel(
        data=data_, name='name', value='value',
        menu_path='test/funnel-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/funnel-test',
        row=1, column=1,
        component_type='funnel',
    )


def test_heatmap():
    data_ = [
        {
            "xAxis": "Lunes",
            "yAxis": "12 a.m",
            "value": 9
        },
        {
            "xAxis": "Lunes",
            "yAxis": "6 p.m",
            "value": 10
        },
        {
            "xAxis": "Lunes",
            "yAxis": "12 p.m",
            "value": 9
        },
        {
            "xAxis": "Lunes",
            "yAxis": "6 a.m",
            "value": 10
        },
        {
            "xAxis": "Martes",
            "yAxis": "12 a.m",
            "value": 9
        },
        {
            "xAxis": "Martes",
            "yAxis": "6 p.m",
            "value": 9
        },
        {
            "xAxis": "Martes",
            "yAxis": "12 p.m",
            "value": 8
        },
        {
            "xAxis": "Martes",
            "yAxis": "6 a.m",
            "value": 0
        },
        {
            "xAxis": "Miercoles",
            "yAxis": "12 a.m",
            "value": 2
        },
        {
            "xAxis": "Miercoles",
            "yAxis": "6 p.m",
            "value": 7
        },
        {
            "xAxis": "Miercoles",
            "yAxis": "12 p.m",
            "value": 0
        },
        {
            "xAxis": "Miercoles",
            "yAxis": "6 a.m",
            "value": 2
        },
        {
            "xAxis": "Jueves",
            "yAxis": "12 a.m",
            "value": 4
        },
        {
            "xAxis": "Jueves",
            "yAxis": "6 p.m",
            "value": 0
        },
        {
            "xAxis": "Jueves",
            "yAxis": "12 p.m",
            "value": 1
        },
        {
            "xAxis": "Jueves",
            "yAxis": "6 a.m",
            "value": 6
        }
    ]
    r = s.plt.heatmap(
        data=data_, x='xAxis', y='yAxis', value='value',
        menu_path='test/heatmap-test',
        row=1, column=1,
    )

    assert r

    s.report.delete_report(
        business_id=business_id,
        app_id=app_id,
        report_id=r['id']
    )


def test_gauge():
    data_ = [
        {
            "value": 60,
            "name": "Third"
        },
        {
            "value": 40,
            "name": "Fourth"
        },
        {
            "value": 20,
            "name": "Fifth"
        },
        {
            "value": 80,
            "name": "Second"
        },
        {
            "value": 100,
            "name": "First"
        }
    ]
    s.plt.gauge(
        data=data_, name='name', value='value',
        menu_path='test/gauge-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/gauge-test',
        component_type='gauge',
        row=1, column=1,
    )


# TODO WiP
def test_sunburst():
    data_ = [
        {
            "name": "Root 1",
            "children": [
                {
                 "name": "Children A",
                 "value": 15,
                 "children": [
                  {
                   "name": "Children A1",
                   "value": 2
                  },
                  {
                   "name": "Chidren AA1",
                   "value": 5,
                   "children": [
                    {
                     "name": "Children AAA1",
                     "value": 2
                    }
                   ]
                  },
                  {
                   "name": "Children A2",
                   "value": 4
                  }
                 ]
                },
                {
                 "name": "Children B",
                 "value": 10,
                 "children": [
                  {
                   "name": "Children B1",
                   "value": 5
                  },
                  {
                   "name": "Children B2",
                   "value": 1
                  }
                 ]
                }
            ]
        },
        {
            "name": "Root 2",
            "children": [
                {
                 "name": "Children A1",
                 "children": [
                  {
                   "name": "Chidren AA1",
                   "value": 1
                  },
                  {
                   "name": "Chidren AA2",
                   "value": 2
                  }
                 ]
                }
            ]
        }
    ]
    r = s.plt.sunburst(
        data=data_, x='xAxis', y=None,  # TODO
        menu_path='test/sunburst-test',
        row=1, column=1,
    )

    assert r

    s.report.delete_report(
        business_id=business_id,
        app_id=app_id,
        report_id=r['id']
    )


def test_tree():
    data_ = [{
        'name': 'root',
        'value': 35,
        'children': [
            {
                'name': 'Child A',
                'value': 9,
                'children': [
                    {'name': 'Child A1', 'value': 23},
                    {'name': 'Child A2', 'value': 72},
                    {'name': 'Child A3', 'value': 93},
                ],
            },
            {
                'name': 'Child B',
                'value': 56,
                'children': [
                    {'name': 'Child B1', 'value': 39},
                    {'name': 'Child B2', 'value': 61},
                    {'name': 'Child B3', 'value': 71},
                ],
            },
            {
                'name': 'Child C',
                'value': 100,
                'children': [
                    {'name': 'Child C1', 'value': 19},
                    {'name': 'Child C2', 'value': 66},
                    {'name': 'Child C3', 'value': 47},
                ],
            },
        ],
    }]
    r = s.plt.tree(
        data=data_,
        menu_path='test/tree-test',
        row=1, column=1,
    )

    assert r

    s.report.delete_report(
        business_id=business_id,
        app_id=app_id,
        report_id=r['id']
    )


def test_treemap():
    data_ = [{
        'name': 'root',
        'value': 35,
        'children': [
            {
                'name': 'Child A',
                'value': 9,
                'children': [
                    {'name': 'Child A1', 'value': 23},
                    {'name': 'Child A2', 'value': 72},
                    {'name': 'Child A3', 'value': 93},
                ],
            },
            {
                'name': 'Child B',
                'value': 56,
                'children': [
                    {'name': 'Child B1', 'value': 39},
                    {'name': 'Child B2', 'value': 61},
                    {'name': 'Child B3', 'value': 71},
                ],
            },
            {
                'name': 'Child C',
                'value': 100,
                'children': [
                    {'name': 'Child C1', 'value': 19},
                    {'name': 'Child C2', 'value': 66},
                    {'name': 'Child C3', 'value': 47},
                ],
            },
        ],
    }]
    r = s.plt.treemap(
        data=data_,
        menu_path='test/treemap-test',
        row=1, column=1,
    )

    assert r

    s.report.delete_report(
        business_id=business_id,
        app_id=app_id,
        report_id=r['id']
    )


def test_radar():
    data_ = [
        {'name': 'Matcha Latte', 'value1': 78, 'value2': 6, 'value3': 85},
        {'name': 'Milk Tea', 'value1': 17, 'value2': 10, 'value3': 63},
        {'name': 'Cheese Cocoa', 'value1': 18, 'value2': 15, 'value3': 65},
        {'name': 'Walnut Brownie', 'value1': 9, 'value2': 71, 'value3': 16},
    ]
    s.plt.radar(
        data=data_,
        x='name', y=['value1', 'value2', 'value3'],
        menu_path='test/radar-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/radar-test',
        component_type='radar',
        row=1, column=1,
    )


def test_indicator():
    data_ = [
        {
            "description": "",
            "title": "Estado",
            "value": "Abierto",
        },
        {
            "description": "",
            "title": "Price ($)",
            "value": "455"
        },
        {
            "description": "",
            "title": "Volumen",
            "value": "41153"
        },
        {
            "description": "",
            "title": "Cambio €/$",
            "value": "1.1946",
        },
    ]
    s.plt.indicator(
        data=data_,
        menu_path='test/indicator-test',
        row=1, column=1,
        value='value',
        header='title',
        footer='description',
    )

    s.plt.delete(
        menu_path='test/indicator-test',
        component_type='indicator',
        row=1, column=1,
    )


def test_alert_indicator():
    data_ = [
        {
            "description": "",
            "title": "Estado",
            "value": "Abierto",
            "color": "warning-background",
            "targetPath": "/whispers-test/test",
        },
        {
            "description": "",
            "title": "Metodo",
            "value": "Entrada",
            "color": "error-background",
            "targetPath": "/whispers-test/test",
        },
    ]
    s.plt.alert_indicator(
        data=data_,
        menu_path='test/indicator-path-test',
        row=1, column=1,
        value='value',
        header='title',
        footer='description',
        color='color',
        target_path='targetPath',
    )

    s.plt.delete(
        menu_path='test/indicator-test',
        row=1, column=1,
        component_type='alert_indicator',
    )


def test_line_with_confidence_area():
    # s.plt.line_with_confidence_area()
    raise NotImplementedError


def test_predictive_line():
    s.plt.predictive_line(
        data=data,
        x='date', y=['x', 'y'],
        min_value_mark=dt.date(2021, 1, 4).isoformat(),
        max_value_mark=dt.date(2021, 1, 5).isoformat(),
        menu_path='test/line-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/line-test',
        row=1, column=1,
    )


# test_bar()
# test_stockline()
# test_line()
# test_predictive_line()
# test_scatter()
# test_funnel()
# test_radar()
# test_gauge()
# test_indicator()
# test_alert_indicator()
test_candlestick()
# TODO
test_scatter_with_confidence_area()
test_bubble_chart()
test_heatmap()
test_sunburst()
test_tree()
test_treemap()
test_line_with_confidence_area()
