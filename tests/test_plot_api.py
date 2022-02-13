""""""
from os import getenv
from typing import Dict, List
import unittest

import datetime as dt
import pandas as pd

import shimoku_api_python as shimoku
from shimoku_api_python.exceptions import ApiClientError


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
    environment=environment,
)
s.plt.set_business(business_id=business_id)


data = [
    {'date': dt.date(2021, 1, 1), 'x': 5, 'y': 5},
    {'date': dt.date(2021, 1, 2), 'x': 6, 'y': 5},
    {'date': dt.date(2021, 1, 3), 'x': 4, 'y': 5},
    {'date': dt.date(2021, 1, 4), 'x': 7, 'y': 5},
    {'date': dt.date(2021, 1, 5), 'x': 3, 'y': 5},
]


def test_ux():
    """
    1. Create single indicator centered
    2. Create single indicator with chart in another column
    """
    menu_path: str = 'test/UX-test'
    data_ = [
        {
            "description": "",
            "title": "Estado",
            "value": "Abierto",
        },
    ]
    s.plt.indicator(
        data=data_,
        menu_path=menu_path,
        row=1, column=1,
        value='value',
        header='title',
        footer='description',
        align='center',
    )

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
    ]
    s.plt.indicator(
        data=data_,
        menu_path=menu_path,
        row=2, column=1,
        value='value',
        header='title',
        footer='description',
    )

    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=2, column=2,
    )

    ###################

    data_ = [
        {
            "description": "",
            "title": "Estado",
            "value": "Abierto",
            "target_path": 'www.shimoku.com',
        },
    ]
    s.plt.alert_indicator(
        data=data_,
        menu_path=menu_path,
        row=3, column=1,
        value='value',
        header='title',
        footer='description',
        target_path='target_path',
    )

    data_ = [
        {
            "description": "",
            "title": "Estado",
            "value": "Abierto",
            "target_path": 'www.shimoku.com',
        },
        {
            "description": "",
            "title": "Price ($)",
            "value": "455",
            "target_path": 'www.shimoku.com',
        },
    ]
    s.plt.alert_indicator(
        data=data_,
        menu_path=menu_path,
        row=4, column=1,
        value='value',
        header='title',
        footer='description',
        target_path='target_path',
    )

    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=4, column=2,
    )


def test_set_path_orders():
    s.plt.set_path_orders(path_order={'test': 1})


def test_set_new_business():
    name: str = 'new-business-test'
    s.plt.set_new_business(name)
    bs = s.universe.get_universe_businesses()
    for b in bs:
        if b['name'] == name:
            s.business.delete_business(b['id'])


def test_delete_path():
    app_path: str = 'test-path'
    menu_path: str = f'{app_path}/line-test'
    menu_path_2: str = f'{app_path}/line-test-2'
    menu_path_3: str = f'{app_path}/line-test-3'

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )
    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=2, column=1,
    )
    app_types: List[Dict] = s.universe.get_universe_app_types()
    app_type_id = max([
        app_type['id']
        for app_type in app_types
        if app_type['normalizedName'] == app_path
    ])
    assert app_type_id
    apps: List[Dict] = s.business.get_business_apps(business_id)
    app_id = max([
        app['id']
        for app in apps
        if app['type']['id'] == app_type_id
    ])

    reports: List[Dict] = s.app.get_app_reports(business_id, app_id)
    assert len(reports) == 2

    s.plt.delete_path(menu_path=menu_path)

    assert len(s.app.get_app_reports(business_id, app_id)) == 0

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )
    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path_2,
        row=1, column=1,
    )
    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path_3,
        row=1, column=1,
    )

    reports: List[Dict] = s.app.get_app_reports(business_id, app_id)
    assert len(reports) == 3

    s.plt.delete_path(menu_path=menu_path)
    reports: List[Dict] = s.app.get_app_reports(business_id, app_id)
    assert len(reports) == 2

    s.plt.delete_path(menu_path=app_path)

    # Check it does not exists anymore
    class MyTestCase(unittest.TestCase):
        def check_reports_not_exists(self):
            with self.assertRaises(ApiClientError):
                s.app.get_app_reports(business_id, app_id)
    t = MyTestCase()
    t.check_reports_not_exists()


def test_delete():
    app_path: str = 'test-delete'
    menu_path: str = f'{app_path}/line-test'

    app_types: List[Dict] = s.universe.get_universe_app_types()
    app_type_id = max([
        app_type['id']
        for app_type in app_types
        if app_type['normalizedName'] == app_path
    ])
    assert app_type_id
    apps: List[Dict] = s.business.get_business_apps(business_id)
    app_id = max([
        app['id']
        for app in apps
        if app['type']['id'] == app_type_id
    ])

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.delete(
        menu_path=menu_path,
        row=1, column=1,
        component_type='line',
    )

    # Check it does not exists anymore
    class MyTestCase(unittest.TestCase):
        def check_reports_not_exists(self):
            with self.assertRaises(ApiClientError):
                s.app.get_app_reports(business_id, app_id)

    t = MyTestCase()
    t.check_reports_not_exists()

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.delete(
        menu_path=menu_path,
        row=1, column=1,
        by_component_type=False,
    )

    # Check it does not exists anymore
    class MyTestCase(unittest.TestCase):
        def check_reports_not_exists(self):
            with self.assertRaises(ApiClientError):
                s.app.get_app_reports(business_id, app_id)

    t = MyTestCase()
    t.check_reports_not_exists()


def test_append_data_to_trend_chart():
    app_path: str = 'test'
    menu_path: str = f'{app_path}/append-test'

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )

    data_ = [
        {'date': dt.date(2021, 1, 6), 'x': 5, 'y': 5},
        {'date': dt.date(2021, 1, 7), 'x': 6, 'y': 5},
    ]

    s.plt.append_data_to_trend_chart(
        menu_path=menu_path,
        row=1, column=1,
        component_type='line',
        data=data_,
        x='date', y=['x', 'y'],
    )

    s.plt.delete(
        menu_path=menu_path,
        row=1, column=1,
        component_type='line',
    )

    # Check it does not exists anymore
    class MyTestCase(unittest.TestCase):
        def check_reports_not_exists(self):
            with self.assertRaises(ApiClientError):
                s.app.get_app_reports(business_id, app_id)

    t = MyTestCase()
    t.check_reports_not_exists()


def test_update():
    menu_path = 'test/update-test'
    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )

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
    s.plt.update(
        data=data_,
        x='date', y=['open', 'close', 'highest', 'lowest'],
        menu_path=menu_path,
        row=1, column=1,
        component_type='bar',
    )

    # Change to linechart
    s.plt.update(
        data=data_,
        x='date', y=['open', 'close', 'highest', 'lowest'],
        menu_path=menu_path,
        row=1, column=1,
        component_type='line',
        by_component_type=False,
    )


def test_table():
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
        menu_path='test/sorted-table-test',
        row=1, column=1,
        filter_columns=filter_columns,
        sort_table_by_col={'date': 'asc'},
    )

    s.plt.delete(
        menu_path='test/sorted-table-test',
        component_type='table',
        row=1, column=1,
    )

    s.plt.table(
        data=data_,
        menu_path='test/table-test',
        row=1, column=1,
        filter_columns=filter_columns,
    )

    s.plt.delete(
        menu_path='test/table-test',
        component_type='table',
        row=1, column=1,
    )


def test_bar_with_filters():
    data_ = pd.read_csv('../data/test_multifilter.csv')
    y: List[str] = [
        'Acné', 'Adeslas', 'Asisa',
        'Aspy', 'Caser', 'Clínica Navarra', 'Cualtis', 'Cáncer', 'DKV',
        'Depresión', 'Dermatólogo', 'Dermatólogo Adeslas', 'Diabetes',
        'Fundación Jiménez Díaz', 'Ginecólogo', 'Ginecólogo Adeslas',
        'HM Hospitales', 'Hemorroides', 'IMQ', 'Preving', 'Psicólogo',
        'Psiquiatra', 'Quirón', 'Quirón Prevención + quirónprevención',
        'Quirón+Quirónsalud', 'Quirónsalud', 'Ruber', 'Ruber Internacional',
        'Ruber Juan Bravo', 'Sanitas', 'Teknon', 'Traumatólogo', 'Vithas'
    ]
    filters: Dict = {
        'exists': False,
        'row': 1, 'column': 1,
        'filter_cols': [
            'seccion', 'frecuencia', 'region',
        ],
    }

    s.plt.bar(
        data=data_,
        x='fecha', y=y,
        menu_path='test/multifilter-bar-test',
        row=1, column=1,
        filters=filters,
    )

    s.plt.delete(
        menu_path='test/multifilter-bar-test',
        component_type='bar',
        row=2, column=1,
    )


def test_bar():
    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/bar-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/bar-test',
        component_type='bar',
        row=1, column=1,
    )


def test_zero_centered_barchart():
    menu_path: str = 'test/zero-centered-bar-test'
    data_ = [
        {'Name': 'a', 'y': 5},
        {'Name': 'b', 'y': -7},
        {'Name': 'c', 'y': 3},
        {'Name': 'd', 'y': -5},
    ]

    s.plt.zero_centered_barchart(
        data=data_,
        x=['y'], y='Name',
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.delete(
        menu_path=menu_path,
        component_type='zero_centered_barchart',
        row=1, column=1,
    )


def test_horizontal_barchart():
    menu_path: str = 'test/horizontal-bar-test'

    data_ = [
        {'Name': 'a', 'y': 5, 'z': 3},
        {'Name': 'b', 'y': 7, 'z': 4},
        {'Name': 'c', 'y': 3, 'z': 5},
        {'Name': 'd', 'y': 5, 'z': 6},
    ]

    s.plt.horizontal_barchart(
        data=data_,
        x=['y', 'z'], y='Name',
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.delete(
        menu_path=menu_path,
        component_type='horizontal_barchart',
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
    s.plt.heatmap(
        data=data_, x='xAxis', y=['yAxis'], value='value',
        menu_path='test/heatmap-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/heatmap-test',
        row=1, column=1,
    )


def test_speed_gauge():
    data_ = [
        {
            "value": 60,
            "name": "Third"
        },
    ]
    s.plt.speed_gauge(
        data=data_, name='name', value='value',
        menu_path='test/speed-gauge-test',
        row=1, column=1,
        min=0, max=70,
    )

    s.plt.delete(
        menu_path='test/speed-gauge-test',
        component_type='speed_gauge',
        row=1, column=1,
    )


def test_ring_gauge():
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
    s.plt.ring_gauge(
        data=data_, name='name', value='value',
        menu_path='test/ring-gauge-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/ring-gauge-test',
        component_type='ring_gauge',
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
                   "name": "Children AA1",
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
                   "name": "Children AA1",
                   "value": 1
                  },
                  {
                   "name": "Children AA2",
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

    s.plt.delete(
        menu_path='test/sunburst-test',
        row=1, column=1,
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
    s.plt.tree(
        data=data_,
        menu_path='test/tree-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/tree-test',
        row=1, column=1,
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
    s.plt.treemap(
        data=data_,
        menu_path='test/treemap-test',
        row=1, column=1,
    )

    s.plt.delete(
        menu_path='test/treemap-test',
        row=1, column=1,
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
            "align": "center",
        },
        {
            "description": "",
            "title": "Price ($)",
            "value": "455",
            "color": "success",
        },
        {
            "description": "this is a description",
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
        align='align',
        color='color'
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


def test_themeriver():
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

    s.plt.delete(
        menu_path='test/themeriver-test',
        component_type='themeriver',
        row=1, column=1,
    )


def test_sankey():
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

    s.plt.delete(
        menu_path='test/sankey-test',
        component_type='sankey',
        row=1, column=1,
    )


def test_pie():
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

    s.plt.delete(
        menu_path='test/pie-test',
        component_type='pie',
        row=1, column=1,
    )


def test_iframe():
    url = 'https://www.marca.com/'
    s.plt.iframe(
        url=url,
        menu_path='test/iframe-test',
        row=1, column=1, order=0,
    )

    s.plt.delete(
        menu_path='test/iframe-test',
        component_type='iframe',
        row=1, column=1,
    )


def test_html():
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

    s.plt.delete(
        menu_path='test/html-test',
        component_type='html',
        row=1, column=1,
    )


def test_cohorts():
    # s.plt.cohort()
    raise NotImplementedError


test_bar_with_filters()
test_table()
test_speed_gauge()
test_bar()
# test_delete_path()
# test_delete()
# test_append_data_to_trend_chart()
# test_ux()
test_indicator()
test_alert_indicator()
# test_set_path_orders()
# test_update()
# test_set_new_business()

test_horizontal_barchart()
test_zero_centered_barchart()
test_stockline()
test_line()
test_predictive_line()
test_scatter()
test_funnel()
test_radar()
test_ring_gauge()
test_indicator()
test_alert_indicator()
test_heatmap()
test_sunburst()
test_tree()
test_treemap()
test_sankey()
test_pie()
test_iframe()
test_html()

# TODO
# test_cohorts()
# test_themeriver()
# test_candlestick()
# test_scatter_with_confidence_area()
# test_bubble_chart()
# test_line_with_confidence_area()
