"""To create all available charts in an App
"""

""""""
from typing import List

import datetime as dt


data = [
    {'date': dt.date(2021, 1, 1), 'x': 5, 'y': 5},
    {'date': dt.date(2021, 1, 2), 'x': 6, 'y': 5},
    {'date': dt.date(2021, 1, 3), 'x': 4, 'y': 5},
    {'date': dt.date(2021, 1, 4), 'x': 7, 'y': 5},
    {'date': dt.date(2021, 1, 5), 'x': 3, 'y': 5},
]


def create_table():
    data_ = [
        {'date': dt.date(2021, 1, 1), 'x': 5, 'y': 5, 'filtA': 'A', 'filtB': 'Z'},
        {'date': dt.date(2021, 1, 2), 'x': 6, 'y': 5, 'filtA': 'B', 'filtB': 'Z'},
        {'date': dt.date(2021, 1, 3), 'x': 4, 'y': 5, 'filtA': 'A', 'filtB': 'W'},
        {'date': dt.date(2021, 1, 4), 'x': 7, 'y': 5, 'filtA': 'B', 'filtB': 'W'},
        {'date': dt.date(2021, 1, 5), 'x': 3, 'y': 5, 'filtA': 'A', 'filtB': 'Z'},
    ]
    filter_columns: List[str] = ['filtA', 'filtB']
    s.plt.table(
        data=data_,
        menu_path='test/table-test',
        row=1, column=1,
        filter_columns=filter_columns,
    )


def create_bar():
    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/bar-test',
        row=1, column=1,
    )


def create_line():
    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/line-test',
        row=1, column=1,
    )


def create_stockline():
    s.plt.stockline(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/stockline-test',
        row=1, column=1,
    )


def create_scatter():
    s.plt.scatter(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/scatter-test',
        row=1, column=1,
    )


def create_funnel():
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


def create_heatmap():
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
    s.plt.heatmap(
        data=data_, x='xAxis', y=['yAxis'], value='value',
        menu_path='test/heatmap-test',
        row=1, column=1,
    )


def create_gauge():
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


def create_sunburst():
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
    s.plt.sunburst(
        data=data_,
        name='xAxis', children='children', value='value',
        menu_path='test/sunburst-test',
        row=1, column=1,
    )


def create_tree():
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
    s.plt.tree(
        data=data_,
        menu_path='test/tree-test',
        row=1, column=1,
    )


def create_treemap():
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
    s.plt.treemap(
        data=data_,
        menu_path='test/treemap-test',
        row=1, column=1,
    )


def create_radar():
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


def create_indicator():
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


def create_alert_indicator():
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


def create_predictive_line():
    s.plt.predictive_line(
        data=data,
        x='date', y=['x', 'y'],
        min_value_mark=dt.date(2021, 1, 4).isoformat(),
        max_value_mark=dt.date(2021, 1, 5).isoformat(),
        menu_path='test/line-test',
        row=1, column=1,
    )


def create_themeriver():
    data_ = [
        {
            "date": "2021/11/08",
            "value": "10",
            "name": "First"
        },
        {
            "date": "2021/11/09",
            "value": "15",
            "name": "First"
        },
        {
            "date": "2021/11/10",
            "value": "35",
            "name": "First"
        },
        {
            "date": "2021/11/11",
            "value": "38",
            "name": "First"
        },
        {
            "date": "2021/11/12",
            "value": "22",
            "name": "First"
        },
        {
            "date": "2021/11/08",
            "value": "35",
            "name": "Second"
        },
        {
            "date": "2021/11/09",
            "value": "36",
            "name": "Second"
        },
        {
            "date": "2021/11/10",
            "value": "37",
            "name": "Second"
        },
        {
            "date": "2021/11/11",
            "value": "22",
            "name": "Second"
        },
        {
            "date": "2021/11/12",
            "value": "24",
            "name": "Second"
        },
        {
            "date": "2021/11/08",
            "value": "21",
            "name": "Third"
        },
        {
            "date": "2021/11/09",
            "value": "25",
            "name": "Third"
        },
        {
            "date": "2021/11/10",
            "value": "27",
            "name": "Third"
        },
        {
            "date": "2021/11/11",
            "value": "23",
            "name": "Third"
        },
        {
            "date": "2021/11/12",
            "value": "24",
            "name": "Third"
        }
    ]
    s.plt.themeriver(
        data=data_,
        x='date', y='value', name='name',
        menu_path='test/themeriver-test',
        row=1, column=1,
    )


def create_sankey():
    data_ = [
        {
            "source": "a",
            "target": "a1",
            "value": 5
        },
        {
            "source": "a",
            "target": "a2",
            "value": 3
        },
        {
            "source": "a",
            "target": "b1",
            "value": 8
        },
        {
            "source": "b",
            "target": "b1",
            "value": 6
        },
        {
            "source": "b1",
            "target": "a1",
            "value": 1
        },
        {
            "source": "b1",
            "target": "c",
            "value": 2
        }
    ]
    s.plt.sankey(
        data=data_,
        source='source', target='target', value='value',
        menu_path='test/sankey-test',
        row=1, column=1,
    )


def create_pie():
    data_ = [
        {'name': 'Matcha Latte', 'value': 78},
        {'name': 'Milk Tea', 'value': 17},
        {'name': 'Cheese Cocoa', 'value': 18},
        {'name': 'Walnut Brownie', 'value': 9},
    ]

    s.plt.pie(
        data=data_,
        x='name', y='value',
        menu_path='test/pie-test',
        row=1, column=1,
    )


def create_iframe():
    url = 'https://www.shimoku.com/'
    s.plt.iframe(
        url=url,
        menu_path='test/iframe-test',
        row=1, column=1, order=0,
    )


def create_html():
    html = (
        "<p style='background-color: #daf4f0';>"
        "Comparing the results of predictions that happened previous "
        "periods vs reality, so that you can measure the accuracy of our predictor"
        "</p>"
    )
    s.plt.html(
        html=html,
        menu_path='test/html-test',
        row=1, column=1,
    )
