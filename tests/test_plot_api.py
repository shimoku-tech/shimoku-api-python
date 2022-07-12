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
delete_paths: bool = False


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
    print('test_ux')
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

    menu_path: str = 'test/UX-test-bysize'
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
        order=0,
        value='value',
        header='title',
        footer='description',
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
        order=1,
        value='value',
        header='title',
        footer='description',
    )

    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=2, rows_size=1, cols_size=6,
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
        order=3, rows_size=2, cols_size=12,
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
        order=4,
        value='value',
        header='title',
        footer='description',
        target_path='target_path',
    )

    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=5, rows_size=1, cols_size=4,
    )


def test_set_apps_orders():
    print('test_set_apps_orders')
    s.plt.set_apps_orders(apps_order={'test': 1, 'caetsu': 2})


def test_set_sub_path_orders():
    print('test_set_sub_path_orders')
    s.plt.set_sub_path_orders(
        paths_order={
            'test/funnel-test': 1,
            'test/tree-test': 2,
        }
    )


def test_set_new_business():
    print('test_set_new_business')
    name: str = 'new-business-test'
    s.plt.set_new_business(name)
    bs = s.universe.get_universe_businesses()
    for b in bs:
        if b['name'] == name:
            s.business.delete_business(b['id'])


def test_delete_path():
    print('test_delete_path')
    app_path: str = 'test-path'
    menu_path: str = f'{app_path}/line-test'
    menu_path_2: str = f'{app_path}/line-test-2'
    menu_path_3: str = f'{app_path}/line-test-3'

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=0,
    )
    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=1,
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
        order=0
    )
    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path_2,
        order=0,
    )
    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path_3,
        order=0,
    )

    reports: List[Dict] = s.app.get_app_reports(business_id, app_id)
    assert len(reports) == 3

    s.plt.delete_path(menu_path=menu_path)
    reports: List[Dict] = s.app.get_app_reports(business_id, app_id)
    assert len(reports) == 2

    s.plt.delete_path(menu_path=app_path)

    # Check it does not exist anymore
    class MyTestCase(unittest.TestCase):
        def check_reports_not_exists(self):
            with self.assertRaises(ApiClientError):
                s.app.get_app_reports(business_id, app_id)
    t = MyTestCase()
    t.check_reports_not_exists()


def test_delete():
    print('test_delete')
    app_path: str = 'test-delete'
    menu_path: str = f'{app_path}/line-test'

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=0,
    )

    app_types: List[Dict] = s.universe.get_universe_app_types()
    app_type_id = max([
        app_type['id']
        for app_type in app_types
        if app_type['normalizedName'] == app_path
    ])
    assert app_type_id
    apps: List[Dict] = s.business.get_business_apps(business_id)
    candidate_app_ids = [
        app['id']
        for app in apps
        if app['type']['id'] == app_type_id
    ]
    if candidate_app_ids:
        app_id = max(candidate_app_ids)
    else:
        app_id = None

    # TODO this must not be here! We must have an app_id! fix the test
    if app_id:
        assert not s.app.get_app_reports(business_id, app_id)

    s.plt.delete(
        menu_path=menu_path,
        order=0,
        component_type='line',
    )

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=0,
    )

    s.plt.delete(
        menu_path=menu_path,
        order=0,
        by_component_type=False,
    )

    # TODO this must not be here! We must have an app_id! fix the test
    if app_id:
        assert not s.app.get_app_reports(business_id, app_id)


def test_append_data_to_trend_chart():
    print('test_append_data_to_trend_chart')
    app_path: str = 'test'
    menu_path: str = f'{app_path}/append-test'

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=f'{menu_path}-bysize',
        order=0, rows_size=2, cols_size=6,
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

    s.plt.append_data_to_trend_chart(
        menu_path=f'{menu_path}-bysize',
        order=0,
        component_type='line',
        data=data_,
        x='date', y=['x', 'y'],
    )

    s.plt.delete(
        menu_path=menu_path,
        row=1, column=1,
        component_type='line',
    )

    s.plt.delete(
        menu_path=f'{menu_path}-bysize',
        order=0,
        component_type='line',
    )


def test_table():
    print('test_table')
    data_ = [
        {'date': dt.date(2021, 1, 1), 'x': 5, 'y': 5, 'filtA': 'A', 'filtB': 'Z', 'name': 'Ana'},
        {'date': dt.date(2021, 1, 2), 'x': 6, 'y': 5, 'filtA': 'B', 'filtB': 'Z', 'name': 'Laura'},
        {'date': dt.date(2021, 1, 3), 'x': 4, 'y': 5, 'filtA': 'A', 'filtB': 'W', 'name': 'Audrey'},
        {'date': dt.date(2021, 1, 4), 'x': 7, 'y': 5, 'filtA': 'B', 'filtB': 'W', 'name': 'Jose'},
        {'date': dt.date(2021, 1, 5), 'x': 3, 'y': 5, 'filtA': 'A', 'filtB': 'Z', 'name': 'Jorge'},
    ]
    filter_columns: List[str] = ['filtA', 'filtB']
    search_columns: List[str] = ['name']

    s.plt.table(
        data=data_,
        menu_path='test/table-test',
        order=1,
        filter_columns=filter_columns,
        sort_table_by_col={'date': 'asc'},
        search_columns=search_columns,
    )

    s.plt.table(
        data=data_,
        menu_path='test/sorted-table-test',
        row=1, column=1,
        filter_columns=filter_columns,
        sort_table_by_col={'date': 'asc'},
    )

    s.plt.table(
        data=data_,
        menu_path='test/table-test',
        row=1, column=1,
        filter_columns=filter_columns,
    )

    if delete_paths:
        s.plt.delete(
            menu_path='test/table-test',
            component_type='table',
            row=1, column=1,
        )

        s.plt.delete(
            menu_path='test/sorted-table-test',
            component_type='table',
            row=1, column=1,
        )

        s.plt.delete(
            menu_path='test/table-test',
            component_type='table',
            row=1, column=1,
        )

        s.plt.delete_path('test/table-test')
        s.plt.delete_path('test/sorted-table-test')


def test_bar_with_filters():
    print('test_bar_with_filters')
    menu_path: str = 'test/multifilter-bar-test'
    # First reset
    # TODO this is because of improvements required for multifilter Update!!
    #  if we remove the delete_path() and we run this method twice it is going to fail!
    s.plt.delete_path(menu_path)
    s.plt.delete_path('multifilter bar test')
    s.plt.delete_path(f'{menu_path}-bysize')
    s.plt.delete_path('multifilter bar test bysize')

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

    data_1 = data_[data_['seccion'].isin(['Empresas hospitalarias', 'Empresas PRL'])]

    filters: Dict = {
        'order': 0,
        'filter_cols': [
            'seccion', 'frecuencia', 'region',
        ],
    }
    s.plt.bar(
        data=data_1,
        x='fecha', y=y,
        menu_path=f'{menu_path}-bysize',
        order=1, rows_size=2,
        cols_size=12,
        filters=filters,
    )

    filters: Dict = {
        'row': 1, 'column': 1,
        'filter_cols': [
            'seccion', 'frecuencia', 'region',
        ],
    }
    s.plt.bar(
        data=data_1,
        x='fecha', y=y,
        menu_path=menu_path,
        row=2, column=1,
        filters=filters,
    )

    data_2 = data_[data_['seccion'].isin(['Enfermedades'])]
    filters: Dict = {
        'update_filter_type': 'concat',
        'row': 1, 'column': 1,
        'filter_cols': [
            'seccion', 'frecuencia', 'region',
        ],
    }

    s.plt.bar(
        data=data_2,
        x='fecha', y=y,
        menu_path=menu_path,
        row=2, column=1,
        filters=filters,
    )

    filters: Dict = {
        'update_filter_type': 'append',
        'row': 1, 'column': 1,
        'filter_cols': [
            'seccion', 'frecuencia', 'region',
        ],
    }

    data_3 = pd.concat([data_1, data_2])
    s.plt.bar(
        data=data_3,
        x='fecha', y=y,
        menu_path=menu_path,
        row=2, column=2,
        filters=filters,
    )

    if delete_paths:
        s.plt.delete_path(menu_path)
        s.plt.delete_path(menu_path=f'{menu_path}-bysize')


def test_bar():
    print('test_bar')
    menu_path = 'test/bar-test'
    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        # row=1, column=1,
        order=0, rows_size=2,
        cols_size=12,
    )
    s.plt.delete_path(menu_path=menu_path)

    menu_path = 'test/bar-test-rowcol'
    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
        order=0, rows_size=2,
        cols_size=12,
    )
    s.plt.delete_path(menu_path=menu_path)

    menu_path = 'test/bar-test'
    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        # row=1, column=1,
        order=1, rows_size=2,
        cols_size=6,
    )
    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        # row=1, column=1,
        order=2, rows_size=2,
        cols_size=4,
        padding="2, 2, 2, 2"
    )

    if delete_paths:
        s.plt.delete_path(menu_path=menu_path)


def test_zero_centered_barchart():
    print('test_zero_centered_barchart')
    menu_path: str = 'test/zero-centered-bar-test'
    data_ = [
        {'Name': 'a', 'y': 5},
        {'Name': 'b', 'y': -7},
        {'Name': 'c', 'y': 3},
        {'Name': 'd', 'y': -5},
    ]

    s.plt.zero_centered_barchart(
        data=data_,
        x='Name', y=['y'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.zero_centered_barchart(
        data=data_,
        x='Name', y=['y'],
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='zero_centered_barchart',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='zero_centered_barchart',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_horizontal_barchart():
    print('test_horizontal_barchart')
    menu_path: str = 'test/horizontal-bar-test'

    data_ = [
        {'Name': 'a', 'y': 5, 'z': 3},
        {'Name': 'b', 'y': 7, 'z': 4},
        {'Name': 'c', 'y': 3, 'z': 5},
        {'Name': 'd', 'y': 5, 'z': 6},
    ]

    s.plt.horizontal_barchart(
        data=data_,
        x='Name', y=['y', 'z'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.horizontal_barchart(
        data=data_,
        x='Name', y=['y', 'z'],
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='horizontal_barchart',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='horizontal_barchart',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_line():
    print('test_line')
    menu_path: str = 'test/line-test'
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
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='line',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='line',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_stockline():
    print('test_stockline')
    menu_path: str = 'test/stockline-test'
    s.plt.stockline(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.stockline(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='stockline',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='stockline',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_scatter():
    print('test_scatter')
    menu_path: str = 'test/scatter-test'
    s.plt.scatter(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.scatter(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='scatter',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='scatter',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_candlestick():
    print('test_candlestick')
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
    print('test_funnel')
    menu_path = 'test/funnel-test'
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
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.funnel(
        data=data_, name='name', value='value',
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='funnel',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='funnel',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_heatmap():
    print('test_heatmap')
    menu_path: str = 'test/heatmap-test'
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
        data=data_, x='xAxis', y='yAxis', value='value',
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.heatmap(
        data=data_, x='xAxis', y='yAxis', value='value',
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='heatmap',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='heatmap',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_speed_gauge():
    print('test_speed_gauge')
    menu_path: str = 'test/speed-gauge-test'
    data_ = [
        {
            "value": 60,
            "name": "Third"
        },
    ]
    s.plt.speed_gauge(
        data=data_, name='name', value='value',
        menu_path=menu_path,
        row=1, column=1,
        min=0, max=70,
    )

    s.plt.speed_gauge(
        data=data_, name='name', value='value', min=0, max=70,
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='speed_gauge',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='speed_gauge',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_ring_gauge():
    print('test_ring_gauge')
    menu_path: str = 'test/ring-gauge-test'
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
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.ring_gauge(
        data=data_, name='name', value='value',
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='ring_gauge',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='ring_gauge',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_sunburst():
    print('test_sunburst')
    menu_path: str = 'test/sunburst-test'
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
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.sunburst(
        data=data_,
        name='xAxis', children='children', value='value',
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='sunburst',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='sunburst',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_tree():
    print('test_tree')
    menu_path: str = 'test/tree-test'
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
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.tree(
        data=data_,
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='tree',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='tree',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_treemap():
    print('test_treemap')
    menu_path: str = 'test/treemap-test'
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
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.treemap(
        data=data_,
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='treemap',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='treemap',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_radar():
    print('test_radar')
    menu_path: str = 'test/radar-test'
    data_ = [
        {'name': 'Matcha Latte', 'value1': 78, 'value2': 6, 'value3': 85},
        {'name': 'Milk Tea', 'value1': 17, 'value2': 10, 'value3': 63},
        {'name': 'Cheese Cocoa', 'value1': 18, 'value2': 15, 'value3': 65},
        {'name': 'Walnut Brownie', 'value1': 9, 'value2': 71, 'value3': 16},
    ]
    s.plt.radar(
        data=data_,
        x='name', y=['value1', 'value2', 'value3'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.radar(
        data=data_,
        x='name', y=['value1', 'value2', 'value3'],
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='radar',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='radar',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_indicator():
    print('test_indicator')
    menu_path: str = 'test/indicator-test'
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
        menu_path=menu_path,
        row=1, column=1,
        value='value',
        header='title',
        footer='description',
        align='align',
        color='color'
    )

    s.plt.indicator(
        data=data_,
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
        value='value',
        header='title',
        footer='description',
        align='align',
        color='color'
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='indicator',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='indicator',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_alert_indicator():
    print('test_alert_indicator')
    menu_path: str = 'test/indicator-path-test'
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
        menu_path=menu_path,
        row=1, column=1,
        value='value',
        header='title',
        footer='description',
        color='color',
        target_path='targetPath',
    )

    s.plt.alert_indicator(
        data=data_,
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
        value='value',
        header='title',
        footer='description',
        color='color',
        target_path='targetPath',
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='indicator',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='indicator',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_predictive_line():
    print('test_predictive_line')
    menu_path: str = 'test/predictive-line-test'
    s.plt.predictive_line(
        data=data,
        x='date', y=['x', 'y'],
        min_value_mark=dt.date(2021, 1, 4).isoformat(),
        max_value_mark=dt.date(2021, 1, 5).isoformat(),
        menu_path='test/predictive-line-test',
        row=1, column=1,
    )

    s.plt.predictive_line(
        data=data,
        x='date', y=['x', 'y'],
        min_value_mark=dt.date(2021, 1, 4).isoformat(),
        max_value_mark=dt.date(2021, 1, 5).isoformat(),
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='predictive_line',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='predictive_line',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_themeriver():
    print('test_themeriver')
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
    print('test_sankey')
    menu_path: str = 'test/sankey-test'
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
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.sankey(
        data=data_,
        source='source', target='target', value='value',
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='sankey',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='sankey',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_pie():
    print('test_pie')
    menu_path: str = 'test/pie-test'
    data_ = [
        {'name': 'Matcha Latte', 'value': 78},
        {'name': 'Milk Tea', 'value': 17},
        {'name': 'Cheese Cocoa', 'value': 18},
        {'name': 'Walnut Brownie', 'value': 9},
    ]

    s.plt.pie(
        data=data_,
        x='name', y='value',
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.pie(
        data=data_,
        x='name', y='value',
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='pie',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='pie',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_iframe():
    print('test_iframe')
    menu_path: str = 'test/iframe-test'
    url = 'https://www.marca.com/'
    s.plt.iframe(
        url=url,
        menu_path=menu_path,
        row=1, column=1, order=0,
    )

    s.plt.iframe(
        url=url,
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='iframe',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='iframe',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_html():
    print('test_html')
    menu_path: str = 'test/html-test'
    html = (
        "<p style='background-color: #daf4f0';>"
        "Comparing the results of predictions that happened previous "
        "periods vs reality, so that you can measure the accuracy of our predictor"
        "</p>"
    )
    s.plt.html(
        html=html,
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.html(
        html=html,
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
    )

    if delete_paths:
        s.plt.delete(
            menu_path=menu_path,
            component_type='html',
            row=1, column=1,
        )
        s.plt.delete(
            menu_path=menu_path,
            component_type='html',
            order=1
        )
        s.plt.delete_path(menu_path)


def test_cohorts():
    print('test_cohorts')
    # s.plt.cohort()
    raise NotImplementedError


print(f'Start time {dt.datetime.now()}')
if delete_paths:
    s.plt.delete_path('test')
test_delete()
test_bar_with_filters()
test_table()
test_set_apps_orders()
test_set_sub_path_orders()
test_zero_centered_barchart()
test_indicator()
test_alert_indicator()
test_stockline()
test_radar()
test_pie()
test_ux()
test_bar()
test_ring_gauge()
test_sunburst()
test_tree()
test_treemap()
test_heatmap()
test_sankey()
test_horizontal_barchart()
test_predictive_line()
test_speed_gauge()
test_line()
test_scatter()
test_funnel()
test_delete_path()
test_append_data_to_trend_chart()
test_iframe()
test_html()
test_set_new_business()


# TODO
# test_cohorts()
# test_themeriver()
# test_candlestick()
# test_scatter_with_confidence_area()
# test_bubble_chart()
# test_line_with_confidence_area()
print(f'End time {dt.datetime.now()}')
