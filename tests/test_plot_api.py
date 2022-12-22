""""""
from os import getenv
from typing import Dict, List
import unittest

import datetime as dt
import pandas as pd
import numpy as np
import random

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
            'Test/Line Test': 3,
        }
    )


def test_set_new_business():
    print('test_set_new_business')
    name: str = 'new-business-test'
    prev_business_id: str = s.plt.business_id

    s.plt.set_new_business(name)
    bs = s.universe.get_universe_businesses()
    for b in bs:
        if b['name'] == name:
            s.business.delete_business(b['id'])

    s.plt.set_business(prev_business_id)


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

    assert s.app.get_app_reports(business_id, app_id)

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

    # Test search columns isolated work
    s.plt.table(
        title="Test-table",
        data=data_,
        menu_path='test/table-test',
        order=1,
        search_columns=search_columns,
    )

    # Test search columns with filters and sorting works
    s.plt.table(
        title="Test-table",
        data=data_,
        menu_path='test/table-test',
        order=1,
        filter_columns=filter_columns,
        sort_table_by_col={'date': 'asc'},
        search_columns=search_columns,
    )

    s.plt.table(
        title="Test-table",
        data=data_,
        menu_path='test/sorted-table-test',
        row=1, column=1,
        filter_columns=filter_columns,
        sort_table_by_col={'date': 'asc'},
    )

    s.plt.table(
        title="Test-table",
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

def test_table_with_labels():
    print("test_table_with_labels")
    menu_path = 'test/table-test-with-labels'

    data_ = [
        {'date': dt.date(2021, 1, 1), 'x': 5, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Ana'   , 'name2': 'Ana'   , 'name3': 'Ana'   },
        {'date': dt.date(2021, 1, 2), 'x': 6, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'Z', 'name': 'Laura' , 'name2': 'Laura' , 'name3': 'Laura' },
        {'date': dt.date(2021, 1, 3), 'x': 4, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'W', 'name': 'Audrey', 'name2': 'Audrey', 'name3': 'Audrey'},
        {'date': dt.date(2021, 1, 4), 'x': 7, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'W', 'name': 'Jose'  , 'name2': 'Jose'  , 'name3': 'Jose'  },
        {'date': dt.date(2021, 1, 5), 'x': 3, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Jorge' , 'name2': 'Jorge' , 'name3': 'Jorge' },
        {'date': dt.date(2021, 1, 1), 'x': 5, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Ana'   , 'name2': 'Ana'   , 'name3': 'Ana'   },
        {'date': dt.date(2021, 1, 2), 'x': 6, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'Z', 'name': 'Laura' , 'name2': 'Laura' , 'name3': 'Laura' },
        {'date': dt.date(2021, 1, 3), 'x': 4, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'W', 'name': 'Audrey', 'name2': 'Audrey', 'name3': 'Audrey'},
        {'date': dt.date(2021, 1, 4), 'x': 7, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'W', 'name': 'Jose'  , 'name2': 'Jose'  , 'name3': 'Jose'  },
        {'date': dt.date(2021, 1, 5), 'x': 3, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Jorge' , 'name2': 'Jorge' , 'name3': 'Jorge' },
        {'date': dt.date(2021, 1, 1), 'x': 5, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Ana'   , 'name2': 'Ana'   , 'name3': 'Ana'   },
        {'date': dt.date(2021, 1, 2), 'x': 6, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'Z', 'name': 'Laura' , 'name2': 'Laura' , 'name3': 'Laura' },
        {'date': dt.date(2021, 1, 3), 'x': 4, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'W', 'name': 'Audrey', 'name2': 'Audrey', 'name3': 'Audrey'},
        {'date': dt.date(2021, 1, 4), 'x': 7, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'W', 'name': 'Jose'  , 'name2': 'Jose'  , 'name3': 'Jose'  },
        {'date': dt.date(2021, 1, 5), 'x': 3, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Jorge' , 'name2': 'Jorge' , 'name3': 'Jorge' },
        {'date': dt.date(2021, 1, 1), 'x': 5, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Ana'   , 'name2': 'Ana'   , 'name3': 'Ana'   },
        {'date': dt.date(2021, 1, 2), 'x': 6, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'Z', 'name': 'Laura' , 'name2': 'Laura' , 'name3': 'Laura' },
        {'date': dt.date(2021, 1, 3), 'x': 4, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'W', 'name': 'Audrey', 'name2': 'Audrey', 'name3': 'Audrey'},
        {'date': dt.date(2021, 1, 4), 'x': 7, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'W', 'name': 'Jose'  , 'name2': 'Jose'  , 'name3': 'Jose'  },
        {'date': dt.date(2021, 1, 5), 'x': 3, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Jorge' , 'name2': 'Jorge' , 'name3': 'Jorge' },
        {'date': dt.date(2021, 1, 1), 'x': 5, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Ana'   , 'name2': 'Ana'   , 'name3': 'Ana'   },
        {'date': dt.date(2021, 1, 2), 'x': 6, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'Z', 'name': 'Laura' , 'name2': 'Laura' , 'name3': 'Laura' },
        {'date': dt.date(2021, 1, 3), 'x': 4, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'W', 'name': 'Audrey', 'name2': 'Audrey', 'name3': 'Audrey'},
        {'date': dt.date(2021, 1, 4), 'x': 7, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'W', 'name': 'Jose'  , 'name2': 'Jose'  , 'name3': 'Jose'  },
        {'date': dt.date(2021, 1, 5), 'x': 3, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Jorge' , 'name2': 'Jorge' , 'name3': 'Jorge' },
        {'date': dt.date(2021, 1, 1), 'x': 5, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Ana'   , 'name2': 'Ana'   , 'name3': 'Ana'   },
        {'date': dt.date(2021, 1, 2), 'x': 6, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'Z', 'name': 'Laura' , 'name2': 'Laura' , 'name3': 'Laura' },
        {'date': dt.date(2021, 1, 3), 'x': 4, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'W', 'name': 'Audrey', 'name2': 'Audrey', 'name3': 'Audrey'},
        {'date': dt.date(2021, 1, 4), 'x': 7, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'B', 'filtB': 'W', 'name': 'Jose'  , 'name2': 'Jose'  , 'name3': 'Jose'  },
        {'date': dt.date(2021, 1, 5), 'x': 3, 'y': round(100 * random.random(), 10),'z': round(100 * random.random(), 1),'a': round(100 * random.random(), 1), 'filtA': 'A', 'filtB': 'Z', 'name': 'Jorge' , 'name2': 'Jorge' , 'name3': 'Jorge' },

    ]

    filter_columns = ['filtA', 'filtB']
    search_columns = ['name']

    s.plt.table(
        data=data_,
        menu_path=menu_path,
        order=16,
        filter_columns=filter_columns,
        sort_table_by_col={'date': 'asc'},
        search_columns=search_columns,
        label_columns={
                    "x": {5: "#666666",
                          6: "#4287f5",
                          4: ("#42F548", "rounded", "filled"),
                          7: [255, 0, 0],
                          3: ([0, 255, 0], "filled"),
                          },
                    "y": {
                        (0, 25): "red",
                        (25, 50): "orange",
                        (50, 75): ("yellow", 'rounded', 'outlined'),
                        (75, np.inf): ("green", "filled", "rounded")
                    },
                    "z": {
                        (0, 25): [100, 100, 100],
                        (25, 50): ("yellow", 'filled'),
                        (50, 75): "orange",
                        (75, np.inf): "red"
                    },
                    "a": {
                        (0, 25): ([100, 100, 100], 'rectangle', 'filled'),
                        (25, 50): "yellow",
                        (50, 75): "orange",
                        (75, np.inf): "red"
                    },
                    "filtA": ("#666666", "filled"),
                    "filtB": [125, 54, 200],
                    "name":  ("warning", 'filled', 'rounded'),
                    "name2": {
                        'Ana'   : ('active', 'rounded', 'filled'),
                        'Laura' : ("error", "filled", "rounded"),
                        'Audrey': ("warning", 'filled', 'rounded'),
                        'Jose'  : ("caution", "outlined"),
                        'Jorge' : ("main", "rounded")
                    },
                    "name3": "neutral"
                    },
        value_suffixes={'y': '%', 'z': '°'}
    )

def test_table_download_csv():
    print('test_table_download_csv')
    data_ = [
        {'date': dt.date(2021, 1, 1), 'x': 5, 'y': 5, 'filtA': 'A', 'filtB': 'Z', 'name': 'Ana'},
        {'date': dt.date(2021, 1, 2), 'x': 6, 'y': 5, 'filtA': 'B', 'filtB': 'Z', 'name': 'Laura'},
        {'date': dt.date(2021, 1, 3), 'x': 4, 'y': 5, 'filtA': 'A', 'filtB': 'W', 'name': 'Audrey'},
        {'date': dt.date(2021, 1, 4), 'x': 7, 'y': 5, 'filtA': 'B', 'filtB': 'W', 'name': 'Jose'},
        {'date': dt.date(2021, 1, 5), 'x': 3, 'y': 5, 'filtA': 'A', 'filtB': 'Z', 'name': 'Jorge'},
    ]

    s.plt.table(
        title="Test-table",
        data=data_,
        menu_path='test/table-test-csv',
        order=1,
        downloadable_to_csv=True
    )

    if delete_paths:
        s.plt.delete(
            menu_path='test/table-test-csv',
            component_type='table',
            row=1, column=1,
        )

        s.plt.delete_path('test/table-test-csv')

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
    data_ = [{'date': dt.date(2021, 1, 1), 'x': 50000000, 'y': 5},
            {'date': dt.date(2021, 1, 2), 'x': 60000000, 'y': 5},
            {'date': dt.date(2021, 1, 3), 'x': 40000000, 'y': 5},
            {'date': dt.date(2021, 1, 4), 'x': 70000000, 'y': 5},
            {'date': dt.date(2021, 1, 5), 'x': 30000000, 'y': 5}]
    s.plt.bar(
        data=data_,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        x_axis_name='Date',
        y_axis_name=['Revenue'],
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


def test_stacked_barchart():
    print("test_stacked_barchart")
    menu_path = 'test/stacked_distribution'
    data_ = pd.read_csv('../data/test_stack_distribution.csv')

    s.plt.stacked_barchart(
        data=data_,
        menu_path=menu_path,
        x="Segment",
        x_axis_name='Distribution and weight of the Drivers',
        order=0,
    )

    s.plt.stacked_barchart(
        data=data_,
        menu_path=menu_path,
        x="Segment",
        x_axis_name='Distribution and weight of the Drivers',
        order=1,
        show_values=['Price'],
        calculate_percentages=True,
    )


def test_stacked_horizontal_barchart():
    print("test_horizontal_stacked_barchart")
    menu_path = 'test/horizontal_stacked_distribution'
    data_ = pd.read_csv('../data/test_stack_distribution.csv')

    s.plt.stacked_horizontal_barchart(
        data=data_,
        menu_path=menu_path,
        x="Segment",
        x_axis_name='Distribution and weight of the Drivers',
        order=0,
    )

    s.plt.stacked_horizontal_barchart(
        data=data_,
        menu_path=menu_path,
        x="Segment",
        x_axis_name='Distribution and weight of the Drivers',
        order=1,
        show_values=['Price'],
        calculate_percentages=True,
    )


def test_stacked_area_chart():
    print("test_area_chart")
    menu_path = 'test/stacked-area-chart'
    data_ = [
        {'Weekday': 'Mon', 'Email': 120, 'Union Ads': 132, 'Video Ads': 101, 'Search Engine': 134},
        {'Weekday': 'Tue', 'Email': 220, 'Union Ads': 182, 'Video Ads': 191, 'Search Engine': 234},
        {'Weekday': 'Wed', 'Email': 150, 'Union Ads': 232, 'Video Ads': 201, 'Search Engine': 154},
        {'Weekday': 'Thu', 'Email': 820, 'Union Ads': 932, 'Video Ads': 901, 'Search Engine': 934},
        {'Weekday': 'Fri', 'Email': 120, 'Union Ads': 132, 'Video Ads': 101, 'Search Engine': 134},
        {'Weekday': 'Sat', 'Email': 220, 'Union Ads': 182, 'Video Ads': 191, 'Search Engine': 234},
        {'Weekday': 'Sun', 'Email': 150, 'Union Ads': 232, 'Video Ads': 201, 'Search Engine': 154},
    ]
    s.plt.stacked_area_chart(
        data=data_,
        menu_path=menu_path,
        x="Weekday",
        x_axis_name='Visits per weekday',
        order=0,
    )

    s.plt.stacked_area_chart(
        data=data_,
        menu_path=menu_path,
        x="Weekday",
        x_axis_name='Visits per weekday',
        order=1,
        show_values=['Search Engine', 'Union Ads'],
        calculate_percentages=True,
    )


def test_zero_centered_barchart():
    print('test_zero_centered_barchart')
    menu_path: str = 'test/zero-centered-bar-test'
    data_ = [
        {'Name': 'a', 'y': 5, 'z': -3, 'a': 0.01},
        {'Name': 'b', 'y': -7, 'z': 4, 'a': 0.1},
        {'Name': 'c', 'y': 3, 'z': -5, 'a': 0.1},
        {'Name': 'd', 'y': -5, 'z': 6, 'a': 0.01},
    ]

    s.plt.zero_centered_barchart(
        data=data_,
        x='Name', y=['y'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.zero_centered_barchart(
        data=data_,
        x='Name', y=['y', 'z', 'a'],
        x_axis_name="Axis x",
        y_axis_name="Axis y",
        title="Title",
        menu_path=menu_path,
        order=1, rows_size=3, cols_size=10,
        padding="0,0,0,1"
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
        {'Name': 'a', 'y': 5, 'z': 3, 'a': 0.01},
        {'Name': 'b', 'y': 7, 'z': 4, 'a': 0.1},
        {'Name': 'c', 'y': 3, 'z': 5, 'a': 0.1},
        {'Name': 'd', 'y': 5, 'z': 6, 'a': 0.01},
    ]

    s.plt.horizontal_barchart(
        data=data_,
        x='Name', y=['y', 'z'],
        menu_path=menu_path,
        row=1, column=1,
    )

    s.plt.horizontal_barchart(
        data=data_,
        x='Name', y=['y', 'z', 'a'],
        x_axis_name="Axis x",
        y_axis_name="Axis y",
        title="Title",
        menu_path=menu_path,
        order=1, rows_size=3, cols_size=10,
        padding="0,0,0,1"
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


def test_doughnut():
    menu_path = 'test/doughnut'
    print('test_doughnut')
    data_ = [
        {'value': 1048, 'name': 'Search Engine'},
        {'value': 735, 'name': 'Direct'},
        {'value': 580, 'name': 'Email'},
        {'value': 484, 'name': 'Union Ads'},
        {'value': 300, 'name': 'Video Ads'}
    ]
    s.plt.doughnut(data_, menu_path=menu_path, order=0)
    s.plt.doughnut(data_, menu_path=menu_path, order=1, rounded=False)

    df = pd.read_csv('../data/test_stack_distribution.csv')
    doughnut_data = pd.DataFrame(columns=["name", "value"])
    df_transposed = df.transpose().reset_index().drop(0)
    value_columns = [col for col in df_transposed.columns if col != "index"]
    doughnut_data["value"] = df_transposed[value_columns].apply(lambda row: sum(row), axis=1)
    doughnut_data["name"] = df_transposed['index']
    s.plt.doughnut(doughnut_data, menu_path=menu_path, order=2,
                   rows_size=3, cols_size=6)


def test_rose():
    menu_path = 'test/rose'
    print('test_rose')
    data_ = [
        {'value': 1048, 'name': 'Search Engine'},
        {'value': 735, 'name': 'Direct'},
        {'value': 580, 'name': 'Email'},
        {'value': 484, 'name': 'Union Ads'},
        {'value': 300, 'name': 'Video Ads'}
    ]
    s.plt.rose(data_, menu_path=menu_path, order=0)
    s.plt.rose(data_, menu_path=menu_path, order=1, rounded=False)

    df = pd.read_csv('../data/test_stack_distribution.csv')
    rose_data = pd.DataFrame(columns=["name", "value"])
    df_transposed = df.transpose().reset_index().drop(0)
    value_columns = [col for col in df_transposed.columns if col != "index"]
    rose_data["value"] = df_transposed[value_columns].apply(lambda row: sum(row), axis=1)
    rose_data["name"] = df_transposed['index']
    s.plt.rose(rose_data, menu_path=menu_path, order=2,
               rows_size=3, cols_size=6)


def test_shimoku_gauges():
    print("test_shimoku_gauges")
    menu_path: str = 'test/shimoku-gauges'
    df = pd.read_csv('../data/test_stack_distribution.csv')
    gauges_data = pd.DataFrame(columns=["name", "value", "color"])
    df_transposed = df.transpose().reset_index().drop(0)
    value_columns = [col for col in df_transposed.columns if col != "index"]
    gauges_data["value"] = df_transposed[value_columns].apply(lambda row: sum(row), axis=1)
    gauges_data["name"] = df_transposed['index']
    gauges_data["color"] = range(1, len(df_transposed) + 1)

    order = s.plt.shimoku_gauges_group(
        gauges_data=gauges_data,
        order=0, menu_path=menu_path,
        cols_size=12, rows_size=3,
        calculate_percentages=True,
    )

    s.plt.shimoku_gauge(
        value=-60, menu_path=menu_path,
        order=order, color=1
    )

    order += 1
    s.plt.shimoku_gauge(
        value=60, menu_path=menu_path, order=order,
        name="test", color="status-error"
    )

    order += 1
    s.plt.shimoku_gauge(
        value=-90, menu_path=menu_path, order=order,
        name="test", color='#FF0000'
    )


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
            "footer": "",
            "header": "Estado",
            "val": "Abierto",
            "alignment": "center",
        },
        {
            "footer": "",
            "header": "Price ($)",
            "val": "455",
            "col": "success",
        },
        {
            "footer": "this is a description",
            "header": "Volumen",
            "val": "41153"
        },
        {
            "footer": "",
            "header": "Cambio €/$",
            "val": "1.1946",
        },
    ]
    s.plt.indicator(
        data=data_,
        menu_path=menu_path,
        row=1, column=1,
        value='val',
        header='header',
        footer='footer',
        align='alignment',
        color='col'
    )

    s.plt.indicator(
        data=data_,
        menu_path=menu_path,
        order=1, rows_size=2, cols_size=12,
        value='val',
        header='header',
        footer='footer',
        align='alignment',
        color='col'
    )
    data_ = [{
        "color": "success",
        "variant": "contained",
        "description": "This indicator has a Link",
        "targetPath": "/indicators/indicator/1",
        "title": "Target Indicator",
        "align": "left",
        "value": "500€"
    }, {
        "color": "warning",
        "backgroundImage": "https://images.unsplash.com/photo-1535957998253-26ae1ef29506?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=736&q=80",
        "variant": "outlined",
        "description": "This has a background",
        "title": "Super cool indicator",
        "align": "left",
        "value": "Value"
    }, {
        "color": "error",
        "variant": "outlined",
        "description": "This hasn't got any icons",
        "title": "Error indicator",
        "align": "left",
        "value": "Value",
    }, {
        "color": "caution",
        "variant": "contained",
        "description": "Aligned to right and full of icons",
        "title": "Multiple cases",
        "align": "right",
        "value": "Value",
    }
    ]
    s.plt.indicator(
        data=data_,
        menu_path=menu_path,
        order=2, rows_size=2, cols_size=12,
        value='value',
        header='title',
        footer='description',
        align='align',
        color='color',
        variant='variant',
        target_path='targetPath',
        background_image='backgroundImage',
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

def test_indicator_one_dict():
    print('test_indicator_one_dict')
    menu_path: str = 'test/indicator-test-one-dict'
    data_ = {
            "description": "",
            "title": "Estado",
            "value": "Abierto",
            "align": "center",
            "color": "warning"
        }

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


def test_bentobox():
    print('test_bentobox')
    menu_path: str = 'test/bentobox-test'

    bentobox_id: Dict = {'bentoboxId': 'test20220101'}
    bentobox_data: Dict = {
        'bentoboxOrder': 0,
        'bentoboxSizeColumns': 8,
        'bentoboxSizeRows': 20,
    }
    bentobox_data.update(bentobox_id)

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
        order=0, rows_size=8, cols_size=12,
        value='value',
        header='title',
        footer='description',
        bentobox_data=bentobox_data,
    )

    s.plt.indicator(
        data=data_,
        menu_path=menu_path,
        order=1, rows_size=8, cols_size=12,
        value='value',
        header='title',
        footer='description',
        bentobox_data=bentobox_id,
    )

    data = [
        {'date': dt.date(2021, 1, 1), 'x': 5, 'y': 5},
        {'date': dt.date(2021, 1, 2), 'x': 6, 'y': 5},
        {'date': dt.date(2021, 1, 3), 'x': 4, 'y': 5},
        {'date': dt.date(2021, 1, 4), 'x': 7, 'y': 5},
        {'date': dt.date(2021, 1, 5), 'x': 3, 'y': 5},
    ]
    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=2, rows_size=14, cols_size=24,
        bentobox_data=bentobox_id,
    )


def test_cohorts():
    print('test_cohorts')
    # s.plt.cohort()
    raise NotImplementedError


def test_free_echarts():
    # https://echarts.apache.org/examples/en/editor.html?c=area-time-axis
    raw_options = """
        {title: {
            text: 'Stacked Area Chart'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross',
              label: {
                backgroundColor: '#6a7985'
              }
            }
          },
          legend: {
            data: ['Email', 'Union Ads', 'Video Ads', 'Direct']
          },
          toolbox: {
            feature: {
              saveAsImage: {}
            }
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: [
            {
              type: 'category',
              boundaryGap: false,
              data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            }
          ],
          yAxis: [
            {
              type: 'value'
            }
          ],
          series: [
            {
              name: 'Email',
              type: 'line',
              stack: 'Total',
              areaStyle: {},
              emphasis: {
                focus: 'series'
              },
              data: [120, 132, 101, 134, 90, 230, 210]
            },
            {
              name: 'Union Ads',
              type: 'line',
              stack: 'Total',
              areaStyle: {},
              emphasis: {
                focus: 'series'
              },
              data: [220, 182, 191, 234, 290, 330, 310]
            },
            {
              name: 'Video Ads',
              type: 'line',
              stack: 'Total',
              areaStyle: {},
              emphasis: {
                focus: 'series'
              },
              data: [150, 232, 201, 154, 190, 330, 410]
            },
            {
              name: 'Direct',
              type: 'line',
              stack: 'Total',
              areaStyle: {},
              emphasis: {
                focus: 'series'
              },
              data: [320, 332, 301, 334, 390, 330, 320]
            },
          ]
        }
    """
    s.plt.free_echarts(
        raw_options=raw_options,
        menu_path='test/raw-free-echarts',
        order=0, rows_size=2, cols_size=12,
    )
    # https://echarts.apache.org/examples/en/editor.html?c=line-marker
    raw_options = """
    {
      title: {
        text: 'Temperature Change in the Coming Week'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {},
      toolbox: {
        show: true,
        feature: {
          dataZoom: {
            yAxisIndex: 'none'
          },
          dataView: { readOnly: false },
          magicType: { type: ['line', 'bar'] },
          restore: {},
          saveAsImage: {}
        }
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value} °C'
        }
      },
      series: [
        {
          name: 'Highest',
          type: 'line',
          data: [10, 11, 13, 11, 12, 12, 9],
          markPoint: {
            data: [
              { type: 'max', name: 'Max' },
              { type: 'min', name: 'Min' }
            ]
          },
          markLine: {
            data: [{ type: 'average', name: 'Avg' }]
          }
        },
        {
          name: 'Lowest',
          type: 'line',
          data: [1, -2, 2, 5, 3, 2, 0],
          markPoint: {
            data: [{ name: '周最低', value: -2, xAxis: 1, yAxis: -1.5 }]
          },
          markLine: {
            data: [
              { type: 'average', name: 'Avg' },
              [
                {
                  symbol: 'none',
                  x: '90%',
                  yAxis: 'max'
                },
                {
                  symbol: 'circle',
                  label: {
                    position: 'start',
                    formatter: 'Max'
                  },
                  type: 'max',
                  name: '最高点'
                }
              ]
            ]
          }
        }
      ]
    };
    """
    s.plt.free_echarts(
        raw_options=raw_options,
        menu_path='test/raw-free-echarts',
        order=1, rows_size=2, cols_size=12,
    )
    # https://echarts.apache.org/examples/en/editor.html?c=line-style
    raw_options = """
        {
      xAxis: {
        type: 'category',
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: [120, 200, 150, 80, 70, 110, 130],
          type: 'line',
          symbol: 'triangle',
          symbolSize: 20,
          lineStyle: {
            color: '#5470C6',
            width: 4,
            type: 'dashed'
          },
          itemStyle: {
            borderWidth: 3,
            borderColor: '#EE6666',
            color: 'yellow'
          }
        }
      ]
    };
    """
    s.plt.free_echarts(
        raw_options=raw_options,
        menu_path='test/raw-free-echarts',
        order=2, rows_size=2, cols_size=12,
    )
    # https://echarts.apache.org/examples/en/editor.html?c=bar-y-category-stack
    raw_options = """
    {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {},
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value'
      },
      yAxis: {
        type: 'category',
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      },
      series: [
        {
          name: 'Direct',
          type: 'bar',
          stack: 'total',
          label: {
            show: true
          },
          emphasis: {
            focus: 'series'
          },
          data: [320, 302, 301, 334, 390, 330, 320]
        },
        {
          name: 'Mail Ad',
          type: 'bar',
          stack: 'total',
          label: {
            show: true
          },
          emphasis: {
            focus: 'series'
          },
          data: [120, 132, 101, 134, 90, 230, 210]
        },
        {
          name: 'Affiliate Ad',
          type: 'bar',
          stack: 'total',
          label: {
            show: true
          },
          emphasis: {
            focus: 'series'
          },
          data: [220, 182, 191, 234, 290, 330, 310]
        },
        {
          name: 'Video Ad',
          type: 'bar',
          stack: 'total',
          label: {
            show: true
          },
          emphasis: {
            focus: 'series'
          },
          data: [150, 212, 201, 154, 190, 330, 410]
        },
      ]
    };
    """
    s.plt.free_echarts(
        raw_options=raw_options,
        menu_path='test/raw-free-echarts',
        order=3, rows_size=2, cols_size=12,
    )
    # https://echarts.apache.org/examples/en/editor.html?c=bar-waterfall2
    # Without functions!
    # Replace "-" by "0"
    raw_options = """
        {      title: {        text: 'Accumulated Waterfall Chart'      },      tooltip: {        trigger: 'axis',        axisPointer: {          type: 'shadow'        },      },      legend: {        data: ['Expenses', 'Income']      },      grid: {        left: '3%',        right: '4%',        bottom: '3%',        containLabel: true      },      xAxis: {        type: 'category',        data:  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]      },      yAxis: {        type: 'value'      },      series: [        {          name: 'Placeholder',          type: 'bar',          stack: 'Total',          itemStyle: {            borderColor: 'transparent',            color: 'transparent'          },          emphasis: {            itemStyle: {              borderColor: 'transparent',              color: 'transparent'            }          },          data: [0, 900, 1245, 1530, 1376, 1376, 1511, 1689, 1856, 1495, 1292]        },        {          name: 'Income',          type: 'bar',          stack: 'Total',          label: {            show: true,            position: 'top'          },          data: [900, 345, 393, 0, 0, 135, 178, 286, 0, 0, 0]        },        {          name: 'Expenses',          type: 'bar',          stack: 'Total',          label: {            show: true,            position: 'bottom'          },          data: [0, 0, 0, 108, 154, 0, 0, 0, 119, 361, 203]        }      ]    };
    """
    s.plt.free_echarts(
        raw_options=raw_options,
        menu_path='test/raw-free-echarts',
        order=4, rows_size=2, cols_size=12,
    )
    # https://echarts.apache.org/examples/en/editor.html?c=pie-roseType-simple
    raw_options = """
    {
      legend: {
        top: 'bottom'
      },
      toolbox: {    
        show: true,
        feature: {
          mark: { show: true },
          dataView: { show: true, readOnly: false },
          restore: { show: true },
          saveAsImage: { show: true }
        }
      },
      series: [
        {
          name: 'Nightingale Chart',
          type: 'pie',
          radius: [50, 250],
          center: ['50%', '50%'],
          roseType: 'area',
          itemStyle: {
            borderRadius: 8
          },
          data: [
            { value: 40, name: 'rose 1' },
            { value: 38, name: 'rose 2' },
            { value: 32, name: 'rose 3' },
            { value: 30, name: 'rose 4' },
            { value: 28, name: 'rose 5' },
            { value: 26, name: 'rose 6' },
            { value: 22, name: 'rose 7' },
            { value: 18, name: 'rose 8' }
          ]
        }
      ]
    };
    """
    s.plt.free_echarts(
        raw_options=raw_options,
        menu_path='test/raw-free-echarts',
        order=5, rows_size=2, cols_size=12,
    )
    # https://echarts.apache.org/examples/en/editor.html?c=pie-borderRadius
    raw_options = """
    {
      tooltip: {
        trigger: 'item'
      },
      legend: {
        top: '5%',
        left: 'center'
      },
      series: [
        {
          name: 'Access From',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '40',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { value: 1048, name: 'Search Engine' },
            { value: 735, name: 'Direct' },
            { value: 580, name: 'Email' },
            { value: 484, name: 'Union Ads' },
            { value: 300, name: 'Video Ads' }
          ]
        }
      ]
    };
    """
    s.plt.free_echarts(
        raw_options=raw_options,
        menu_path='test/raw-free-echarts',
        order=6, rows_size=4, cols_size=8,
    )
    # https://echarts.apache.org/examples/en/editor.html?c=radar
    raw_options = """
    {
      title: {
        text: 'Basic Radar Chart'
      },
      legend: {
        data: ['Allocated Budget', 'Actual Spending']
      },
      radar: {
        indicator: [
          { name: 'Sales', max: 6500 },
          { name: 'Administration', max: 16000 },
          { name: 'Information Technology', max: 30000 },
          { name: 'Customer Support', max: 38000 },
          { name: 'Development', max: 52000 },
          { name: 'Marketing', max: 25000 }
        ]
      },
      series: [
        {
          name: 'Budget vs spending',
          type: 'radar',
          data: [
            {
              value: [4200, 3000, 20000, 35000, 50000, 18000],
              name: 'Allocated Budget'
            },
            {
              value: [5000, 14000, 28000, 26000, 42000, 21000],
              name: 'Actual Spending'
            }
          ]
        }
      ]
    };
    """
    s.plt.free_echarts(
        raw_options=raw_options,
        menu_path='test/raw-free-echarts',
        order=7, rows_size=3, cols_size=8,
    )
    # https://echarts.apache.org/examples/en/editor.html?c=gauge-speed
    raw_options = """{
      series: [
        {
          type: 'gauge',
          progress: {
            show: true,
            width: 18
          },
          axisLine: {
            lineStyle: {
              width: 18
            }
          },
          axisTick: {
            show: false
          },
          splitLine: {
            length: 15,
            lineStyle: {
              width: 2,
              color: '#999'
            }
          },
          axisLabel: {
            distance: 25,
            color: '#999',
            fontSize: 20
          },
          anchor: {
            show: true,
            showAbove: true,
            size: 25,
            itemStyle: {
              borderWidth: 10
            }
          },
          title: {
            show: false
          },
          detail: {
            valueAnimation: true,
            fontSize: 80,
            offsetCenter: [0, '70%']
          },
          data: [
            {
              value: 70
            }
          ]
        }
      ]
    };
    """
    s.plt.free_echarts(
        raw_options=raw_options,
        menu_path='test/raw-free-echarts',
        order=8, rows_size=3, cols_size=8,
    )
    # TODO pendings
    #  https://echarts.apache.org/examples/en/editor.html?c=sunburst-visualMap
    #  https://echarts.apache.org/examples/en/editor.html?c=data-transform-aggregate
    #  https://echarts.apache.org/examples/en/editor.html?c=custom-ohlc
    #  https://echarts.apache.org/examples/en/editor.html?c=scatter-clustering

    print('Raw free echarts finished')

    data = [
        {'product': 'Matcha Latte', '2015': 43.3, '2016': 85.8, '2017': 93.7},
        {'product': 'Milk Tea', '2015': 83.1, '2016': 73.4, '2017': 55.1},
        {'product': 'Cheese Cocoa', '2015': 86.4, '2016': 65.2, '2017': 82.5},
        {'product': 'Walnut Brownie', '2015': 72.4, '2016': 53.9, '2017': 39.1}
    ]
    options = {
        'legend': {},
        'tooltip': {},
        'xAxis': {'type': 'category'},
        'yAxis': {},
        'series': [{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]
    }
    s.plt.free_echarts(
        data=data,
        options=options,
        menu_path='test/free-echarts',
        order=0, rows_size=2, cols_size=12,
    )

    # https://echarts.apache.org/examples/en/editor.html?c=area-stack
    data = [
        {'Mon': 120, 'Tue': 132, 'Wed': 101, 'Thu': 134},  # , 'Fri': 90, 'Sat': 230, 'Sun': 210},
        {'Mon': 220, 'Tue': 182, 'Wed': 191, 'Thu': 234},  # , 'Fri': 290, 'Sat': 330, 'Sun': 310},
        {'Mon': 150, 'Tue': 232, 'Wed': 201, 'Thu': 154},  # , 'Fri': 190, 'Sat': 330, 'Sun': 410},
        {'Mon': 820, 'Tue': 932, 'Wed': 901, 'Thu': 934},  # , 'Fri': 1290, 'Sat': 1330, 'Sun': 1320}
    ]
    data = [
            {'Weekday': 'Mon', 'Email': 120, 'Union Ads': 132, 'Video Ads': 101, 'Search Engine': 134},
            {'Weekday': 'Tue', 'Email': 220, 'Union Ads': 182, 'Video Ads': 191, 'Search Engine': 234},
            {'Weekday': 'Wed', 'Email': 150, 'Union Ads': 232, 'Video Ads': 201, 'Search Engine': 154},
            {'Weekday': 'Thu', 'Email': 820, 'Union Ads': 932, 'Video Ads': 901, 'Search Engine': 934},
            {'Weekday': 'Fri', 'Email': 120, 'Union Ads': 132, 'Video Ads': 101, 'Search Engine': 134},
            {'Weekday': 'Sat', 'Email': 220, 'Union Ads': 182, 'Video Ads': 191, 'Search Engine': 234},
            {'Weekday': 'Sun', 'Email': 150, 'Union Ads': 232, 'Video Ads': 201, 'Search Engine': 154},
    ]
    options = {
        'title': {'text': 'Stacked Area Chart'},
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {
                'type': 'cross',
                'label': {'backgroundColor': '#6a7985'}
            }
        },
        'legend': {
            'data': ['Email', 'Union Ads', 'Video Ads', 'Search Engine']
        },
        'toolbox': {
            'feature': {
                'saveAsImage': {}
            }
        },
        'grid': {
            'left': '3%',
            'right': '4%',
            'bottom': '3%',
            'containLabel': True
        },
        'xAxis': [{
          'type': 'category',
          'boundaryGap': False,
        }],
        'yAxis': [{'type': 'value'}],
        'series': [{
            'name': 'Email',
            'type': 'line',
            'stack': 'Total',
            'areaStyle': {},
            'emphasis': {'focus': 'series'},
        }, {
            'name': 'Union Ads',
            'type': 'line',
            'stack': 'Total',
            'areaStyle': {},
            'emphasis': {'focus': 'series'},
        }, {
            'name': 'Video Ads',
            'type': 'line',
            'stack': 'Total',
            'areaStyle': {},
            'emphasis': {'focus': 'series'},
        }, {
            'name': 'Search Engine',
            'type': 'line',
            'stack': 'Total',
            'label': {
                'show': True,
                'position': 'top'
            },
            'areaStyle': {},
            'emphasis': {'focus': 'series'},
        }]
    }
    for i in range(len(data)):
        data[i]['sort_values'] = i
    s.plt.free_echarts(
        data=data,
        options=options,
        menu_path='test/free-echarts',
        order=1, rows_size=2, cols_size=12,
        sort={
            'field': 'sort_values',
            'direction': 'asc',
        }
    )

    # https://echarts.apache.org/examples/en/editor.html?c=bar-waterfall
    data = [
        ['Total', 'Rent', 'Utilities', 'Transportation', 'Meals', 'Other'],
        [0, 1700, 1400, 1200, 300, 0],
        [2900, 1200, 300, 200, 900, 300],
    ]
    data = [
        {'Type': 'Total', 'Placeholder': 0, 'Life Cost': 2900},
        {'Type': 'Rent', 'Placeholder': 1700, 'Life Cost': 1200},
        {'Type': 'Utilities', 'Placeholder': 1400, 'Life Cost': 300},
        {'Type': 'Transportation', 'Placeholder': 1200, 'Life Cost': 200},
        {'Type': 'Meals', 'Placeholder': 300, 'Life Cost': 900},
        {'Type': 'Other', 'Placeholder': 0, 'Life Cost': 300},
    ]
    options = {
        'title': {
            'text': 'Waterfall Chart',
            'subtext': 'Living Expenses in Shenzhen'
        },
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {
                'type': 'shadow'
            },
        },
        'grid': {
            'left': '3%',
            'right': '4%',
            'bottom': '3%',
            'containLabel': True
        },
        'xAxis': {
            'type': 'category',
            'splitLine': {'show': False},
        },
        'yAxis': {'type': 'value'},
        'series': [
            {
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
            },
            {
                'name': 'Life Cost',
                'type': 'bar',
                'stack': 'Total',
                'label': {
                    'show': True,
                    'position': 'inside'
                },
            }
        ]
    }
    for i in range(len(data)):
        data[i]['sort_values'] = i
    s.plt.free_echarts(
        data=data,
        options=options,
        menu_path='test/free-echarts',
        order=2, rows_size=2, cols_size=6,
        sort={
            'field': 'sort_values',
            'direction': 'desc',
        }
    )

    # https://echarts.apache.org/examples/en/editor.html?c=bar-polar-stack-radial
    data = [
        ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        [1, 2, 3, 4, 3, 5, 1],
        [2, 4, 6, 1, 3, 2, 1],
        [1, 2, 3, 4, 1, 2, 5],
    ]
    data = [
        {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4},
        {'Mon': 2, 'Tue': 4, 'Wed': 6, 'Thu': 1},
        {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4},
    ]
    data = [
        {'Weekday': 'Mon', 'A': 1, 'B': 2, 'C': 1},
        {'Weekday': 'Tue', 'A': 2, 'B': 4, 'C': 2},
        {'Weekday': 'Wed', 'A': 3, 'B': 6, 'C': 3},
        {'Weekday': 'Thu', 'A': 4, 'B': 1, 'C': 4},
        {'Weekday': 'Fri', 'A': 4, 'B': 1, 'C': 4},
        {'Weekday': 'Sat', 'A': 4, 'B': 1, 'C': 4},
        {'Weekday': 'Sun', 'A': 4, 'B': 1, 'C': 4},
    ]
    options = {
        'angleAxis': {'type': 'category'},
        'radiusAxis': {},
        'polar': {},
        'series': [
            {
                'type': 'bar',
                'coordinateSystem': 'polar',
                'name': 'A',
                'stack': 'a',
                'emphasis': {'focus': 'series'}
            },
            {
                'type': 'bar',
                'coordinateSystem': 'polar',
                'name': 'B',
                'stack': 'a',
                'emphasis': {'focus': 'series'}
            },
            {
                'type': 'bar',
                'coordinateSystem': 'polar',
                'name': 'C',
                'stack': 'a',
                'emphasis': {'focus': 'series'}
            }
        ],
        'legend': {
            'show': True,
            'data': ['A', 'B', 'C']
        }
    }
    for i in range(len(data)):
        data[i]['sort_values'] = i
    s.plt.free_echarts(
        data=data,
        options=options,
        menu_path='test/free-echarts',
        order=3, rows_size=2, cols_size=6,
        sort={
            'field': 'sort_values',
            'direction': 'asc',
        }
    )

    # https://echarts.apache.org/examples/en/editor.html?c=pie-borderRadius
    data = [
        {'value': 1048, 'name': 'Search Engine'},
        {'value': 735, 'name': 'Direct'},
        {'value': 580, 'name': 'Email'},
        {'value': 484, 'name': 'Union Ads'},
        {'value': 300, 'name': 'Video Ads'}
    ]
    options = {
        'tooltip': {'trigger': 'item'},
        'legend': {
            'top': '5%',
            'left': 'center'
        },
        'series': [
            {
                'name': 'Access From',
                'type': 'pie',
                'radius': ['40%', '70%'],
                'avoidLabelOverlap': False,
                'itemStyle': {
                    'borderRadius': 10,
                    'borderColor': '#fff',
                    'borderWidth': 2
                },
                'label': {
                    'show': False,
                    'position': 'center'
                },
                'emphasis': {
                    'label': {
                        'show': True,
                        'fontSize': '40',
                        'fontWeight': 'bold'
                    }
                },
                'labelLine': {'show': False},
            }]
        }
    s.plt.free_echarts(
        data=data,
        options=options,
        menu_path='test/free-echarts',
        order=4, rows_size=2, cols_size=6,
    )

    data = [
        {'product': 'Matcha Latte', '2015': 43.3, '2016': 85.8},
        {'product': 'Milk Tea', '2015': 83.1, '2016': 73.4},
        {'product': 'Cheese Cocoa', '2015': 86.4, '2016': 65.2},
        {'product': 'Walnut Brownie', '2015': 72.4, '2016': 53.9},
        {'product': 'Cold brew', '2015': 43.3, '2016': 85.8},
        {'product': 'Espresso', '2015': 83.1, '2016': 73.4},
        {'product': 'Kombucola', '2015': 86.4, '2016': 65.2},
    ]
    options = {
        'legend': {},
        'tooltip': {},
        'xAxis': {'type': 'category'},
        'yAxis': {},
        'series': [{'type': 'bar'}, {'type': 'line'}]
    }
    s.plt.free_echarts(
        data=data,
        options=options,
        menu_path='test/free-echarts',
        order=5, rows_size=2, cols_size=6,
    )

    # TODO it is not showing the normal & outliers simultaneously
    # https://echarts.apache.org/examples/en/editor.html?c=scatter-effect
    data = [
        # shining dots
        [172.7, 105.2], [153.4, 42],
        # the rest
        [161.2, 51.6], [167.5, 59.0], [159.5, 49.2], [157.0, 63.0], [155.8, 53.6],
        [170.0, 59.0], [159.1, 47.6], [166.0, 69.8], [176.2, 66.8], [160.2, 75.2],
        [172.5, 55.2], [170.9, 54.2], [172.9, 62.5], [153.4, 42.0], [160.0, 50.0],
        [147.2, 49.8], [168.2, 49.2], [175.0, 73.2], [157.0, 47.8], [167.6, 68.8],
        [159.5, 50.6], [175.0, 82.5], [166.8, 57.2], [176.5, 87.8], [170.2, 72.8],
        [174.0, 54.5], [173.0, 59.8], [179.9, 67.3], [170.5, 67.8], [160.0, 47.0],
    ]
    data = [
        {'x': 172.7, 'y': 105.2},
        {'x': 153.4, 'y': 42.0},
        {'x': 161.2, 'y': 51.6},
        {'x': 167.5, 'y': 59.0},
        {'x': 159.5, 'y': 49.2},
        {'x': 157.0, 'y': 63.0},
        {'x': 155.8, 'y': 53.6},
        {'x': 170.0, 'y': 59.0},
        {'x': 159.1, 'y': 47.6},
        {'x': 166.0, 'y': 69.8},
        {'x': 176.2, 'y': 66.8},
        {'x': 160.2, 'y': 75.2},
        {'x': 172.5, 'y': 55.2},
        {'x': 170.9, 'y': 54.2},
        {'x': 172.9, 'y': 62.5},
        {'x': 153.4, 'y': 42.0},
        {'x': 160.0, 'y': 50.0},
        {'x': 147.2, 'y': 49.8},
        {'x': 168.2, 'y': 49.2},
        {'x': 175.0, 'y': 73.2},
        {'x': 157.0, 'y': 47.8},
        {'x': 167.6, 'y': 68.8},
        {'x': 159.5, 'y': 50.6},
        {'x': 175.0, 'y': 82.5},
        {'x': 166.8, 'y': 57.2},
        {'x': 176.5, 'y': 87.8},
        {'x': 170.2, 'y': 72.8},
        {'x': 174.0, 'y': 54.5},
        {'x': 173.0, 'y': 59.8},
        {'x': 179.9, 'y': 67.3},
        {'x': 170.5, 'y': 67.8},
        {'x': 160.0, 'y': 47.0}
    ]
    data = [
        {'x': 172.7, 'y': 105.2, 'x2': 153.4, 'y2': 42.0},
        {'x': 161.2, 'y': 51.6, 'x2': 167.5, 'y2': 59.0},
        {'x': 161.2, 'y': 51.6, 'x2': 150, 'y2': 20},
        {'x': 150, 'y': 20, 'x2': 157.0, 'y2': 63.0},
        {'x': 150, 'y': 20, 'x2': 155.8, 'y2': 53.6},
        {'x': 150, 'y': 20, 'x2': 170.0, 'y2': 59.0},
        {'x': 150, 'y': 20, 'x2': 159.1, 'y2': 47.6},
        {'x': 150, 'y': 20, 'x2': 166.0, 'y2': 69.8},
        {'x': 150, 'y': 20, 'x2': 176.2, 'y2': 66.8},
        {'x': 150, 'y': 20, 'x2': 160.2, 'y2': 75.2},
        {'x': 150, 'y': 20, 'x2': 172.5, 'y2': 55.2},
        {'x': 150, 'y': 20, 'x2': 170.9, 'y2': 54.2},
        {'x': 150, 'y': 20, 'x2': 172.9, 'y2': 62.5},
        {'x': 150, 'y': 20, 'x2': 153.4, 'y2': 42.0},
        {'x': 150, 'y': 20, 'x2': 160.0, 'y2': 50.0},
        {'x': 150, 'y': 20, 'x2': 147.2, 'y2': 49.8},
    ]
    options = {
        'xAxis': {'scale': True},
        'yAxis': {'scale': True},
        'series': [
            {'type': 'effectScatter', 'symbolSize': 20},
            {'type': 'scatter'},
        ]
    }
    s.plt.free_echarts(
        data=data,
        options=options,
        menu_path='test/free-echarts',
        order=6, rows_size=2, cols_size=7,
    )

    data = [
        {'product': 'Matcha Latte', '2015': 43.3, '2016': 85.8, '2017': 93.7},
        {'product': 'Milk Tea', '2015': 83.1, '2016': 73.4, '2017': 55.1},
        {'product': 'Cheese Cocoa', '2015': 86.4, '2016': 65.2, '2017': 82.5},
        {'product': 'Walnut Brownie', '2015': 72.4, '2016': 53.9, '2017': 39.1}
    ]
    options = {
        'legend': {},
        'tooltip': {},
        'xAxis': {'type': 'category'},
        'yAxis': {},
        'series': [{'type': 'bar'}, {'type': 'line'}, {'type': 'bar'}]
    }
    s.plt.free_echarts(
        data=data,
        options=options,
        menu_path='test/free-echarts',
        order=7, rows_size=2, cols_size=5,
    )

    print('Free echarts finished')

    # TODO no funca!!
    """
    # https://echarts.apache.org/examples/en/editor.html?c=themeRiver-basic
    data = [
        ['2015/11/08', 10, 'DQ'],
        ['2015/11/09', 15, 'DQ'],
        ['2015/11/10', 35, 'DQ'],
        ['2015/11/11', 38, 'DQ'],
        ['2015/11/12', 22, 'DQ'],
        ['2015/11/13', 16, 'DQ'],
        ['2015/11/14', 7, 'DQ'],
        ['2015/11/15', 2, 'DQ'],
        ['2015/11/16', 17, 'DQ'],
        ['2015/11/17', 33, 'DQ'],
        ['2015/11/18', 40, 'DQ'],
        ['2015/11/19', 32, 'DQ'],
        ['2015/11/20', 26, 'DQ'],
        ['2015/11/21', 35, 'DQ'],
        ['2015/11/22', 40, 'DQ'],
        ['2015/11/23', 32, 'DQ'],
        ['2015/11/24', 26, 'DQ'],
        ['2015/11/25', 22, 'DQ'],
        ['2015/11/26', 16, 'DQ'],
        ['2015/11/27', 22, 'DQ'],
        ['2015/11/28', 10, 'DQ'],
        ['2015/11/08', 35, 'TY'],
        ['2015/11/09', 36, 'TY'],
        ['2015/11/10', 37, 'TY'],
        ['2015/11/11', 22, 'TY'],
        ['2015/11/12', 24, 'TY'],
        ['2015/11/13', 26, 'TY'],
        ['2015/11/14', 34, 'TY'],
        ['2015/11/15', 21, 'TY'],
        ['2015/11/16', 18, 'TY'],
        ['2015/11/17', 45, 'TY'],
        ['2015/11/18', 32, 'TY'],
        ['2015/11/19', 35, 'TY'],
        ['2015/11/20', 30, 'TY'],
        ['2015/11/21', 28, 'TY'],
        ['2015/11/22', 27, 'TY'],
        ['2015/11/23', 26, 'TY'],
        ['2015/11/24', 15, 'TY'],
        ['2015/11/25', 30, 'TY'],
        ['2015/11/26', 35, 'TY'],
        ['2015/11/27', 42, 'TY'],
        ['2015/11/28', 42, 'TY'],
        ['2015/11/08', 21, 'SS'],
        ['2015/11/09', 25, 'SS'],
        ['2015/11/10', 27, 'SS'],
        ['2015/11/11', 23, 'SS'],
        ['2015/11/12', 24, 'SS'],
        ['2015/11/13', 21, 'SS'],
        ['2015/11/14', 35, 'SS'],
        ['2015/11/15', 39, 'SS'],
        ['2015/11/16', 40, 'SS'],
        ['2015/11/17', 36, 'SS'],
        ['2015/11/18', 33, 'SS'],
        ['2015/11/19', 43, 'SS'],
        ['2015/11/20', 40, 'SS'],
        ['2015/11/21', 34, 'SS'],
        ['2015/11/22', 28, 'SS'],
        ['2015/11/23', 26, 'SS'],
        ['2015/11/24', 37, 'SS'],
        ['2015/11/25', 41, 'SS'],
        ['2015/11/26', 46, 'SS'],
        ['2015/11/27', 47, 'SS'],
        ['2015/11/28', 41, 'SS'],
        ['2015/11/08', 10, 'QG'],
        ['2015/11/09', 15, 'QG'],
        ['2015/11/10', 35, 'QG'],
        ['2015/11/11', 38, 'QG'],
        ['2015/11/12', 22, 'QG'],
        ['2015/11/13', 16, 'QG'],
        ['2015/11/14', 7, 'QG'],
        ['2015/11/15', 2, 'QG'],
        ['2015/11/16', 17, 'QG'],
        ['2015/11/17', 33, 'QG'],
        ['2015/11/18', 40, 'QG'],
        ['2015/11/19', 32, 'QG'],
        ['2015/11/20', 26, 'QG'],
        ['2015/11/21', 35, 'QG'],
        ['2015/11/22', 40, 'QG'],
        ['2015/11/23', 32, 'QG'],
        ['2015/11/24', 26, 'QG'],
        ['2015/11/25', 22, 'QG'],
        ['2015/11/26', 16, 'QG'],
        ['2015/11/27', 22, 'QG'],
        ['2015/11/28', 10, 'QG'],
        ['2015/11/08', 10, 'SY'],
        ['2015/11/09', 15, 'SY'],
        ['2015/11/10', 35, 'SY'],
        ['2015/11/11', 38, 'SY'],
        ['2015/11/12', 22, 'SY'],
        ['2015/11/13', 16, 'SY'],
        ['2015/11/14', 7, 'SY'],
        ['2015/11/15', 2, 'SY'],
        ['2015/11/16', 17, 'SY'],
        ['2015/11/17', 33, 'SY'],
        ['2015/11/18', 40, 'SY'],
        ['2015/11/19', 32, 'SY'],
        ['2015/11/20', 26, 'SY'],
        ['2015/11/21', 35, 'SY'],
        ['2015/11/22', 4, 'SY'],
        ['2015/11/23', 32, 'SY'],
        ['2015/11/24', 26, 'SY'],
        ['2015/11/25', 22, 'SY'],
        ['2015/11/26', 16, 'SY'],
        ['2015/11/27', 22, 'SY'],
        ['2015/11/28', 10, 'SY'],
        ['2015/11/08', 10, 'DD'],
        ['2015/11/09', 15, 'DD'],
        ['2015/11/10', 35, 'DD'],
        ['2015/11/11', 38, 'DD'],
        ['2015/11/12', 22, 'DD'],
        ['2015/11/13', 16, 'DD'],
        ['2015/11/14', 7, 'DD'],
        ['2015/11/15', 2, 'DD'],
        ['2015/11/16', 17, 'DD'],
        ['2015/11/17', 33, 'DD'],
        ['2015/11/18', 4, 'DD'],
        ['2015/11/19', 32, 'DD'],
        ['2015/11/20', 26, 'DD'],
        ['2015/11/21', 35, 'DD'],
        ['2015/11/22', 40, 'DD'],
        ['2015/11/23', 32, 'DD'],
        ['2015/11/24', 26, 'DD'],
        ['2015/11/25', 22, 'DD'],
        ['2015/11/26', 16, 'DD'],
        ['2015/11/27', 22, 'DD'],
        ['2015/11/28', 10, 'DD']
    ]
    data = [
        {'date': 1, 'DQ': 15, 'TY': 36, 'SS': 25},
        {'date': 2, 'DQ': 15, 'TY': 36, 'SS': 25},
        {'date': 3, 'DQ': 15, 'TY': 36, 'SS': 25},
        {'date': 4, 'DQ': 15, 'TY': 36, 'SS': 25},
        {'date': 5, 'DQ': 15, 'TY': 36, 'SS': 25},
        {'date': 6, 'DQ': 15, 'TY': 36, 'SS': 25},
    ]
    options = {
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {
                'type': 'line',
                'lineStyle': {
                    'color': 'rgba(0,0,0,0.2)',
                    'width': 1,
                    'type': 'solid'
                }
            }
        },
        'legend': {
            'data': ['DQ', 'TY', 'SS']
        },
        'singleAxis': {
            'top': 50,
            'bottom': 50,
            'axisTick': {},
            'axisLabel': {},
            'type': 'time',
            'axisPointer': {
                'animation': True,
                'label': {'show': True}
            },
            'splitLine': {
                'show': True,
                'lineStyle': {
                    'type': 'dashed',
                    'opacity': 0.2
                }
            }
        },
        'series': [
            {
                'type': 'themeRiver',
                'emphasis': {
                    'itemStyle': {
                        'shadowBlur': 20,
                        'shadowColor': 'rgba(0, 0, 0, 0.8)'
                    }
                },
            }
        ]
    }
    s.plt.free_echarts(
        data=data,
        options=options,
        menu_path='test/free-echarts',
        order=8, rows_size=2, cols_size=6,
        sort={
            'field': 'date',
            'direction': 'asc',
        }
    )
    """


def test_input_form():
    report_dataset_properties = {
      'fields': [
        {
          'title': 'Personal information',
          'fields': [
            {
                'mapping': 'name',
                'fieldName': 'name',
                'inputType': 'text',
              },
              {
                'mapping': 'surname',
                'fieldName': 'surname',
                'inputType': 'text',
              },
            {
              'mapping': 'age',
              'fieldName': 'age',
              'inputType': 'number',
            },
            {
                'mapping': 'tel',
                'fieldName': 'phone',
                'inputType': 'tel',
              },
              {
                'mapping': 'gender',
                'fieldName': 'Gender',
                'inputType': 'radio',
                'options': ['Male', 'Female', 'No-binary', 'Undefined'],
              },
            {
                'mapping': 'email',
                'fieldName': 'email',
                'inputType': 'email',
              },

          ],
        },
        {
          'title': 'Other data',
          'fields': [
            {
              'mapping': 'skills',
              'fieldName': 'Skills',
              'options': ['Backend', 'Frontend', 'UX/UI', 'Api Builder', 'DevOps'],
              'inputType': 'checkbox',
            },
            {
                'mapping': 'birthDay',
                'fieldName': 'Birthday',
                'inputType': 'date',
              },
              {
                'mapping': 'onCompany',
                'fieldName': 'Time on Shimoku',
                'inputType': 'dateRange',
              },
              {
                'mapping': 'hobbies',
                'fieldName': 'Hobbies',
                'inputType': 'select',
                'options': ['Make Strong Api', 'Sailing to Canarias', 'Send Abracitos'],
              },
              {
                'mapping': 'textField2',
                'fieldName': 'Test Text',
                'inputType': 'text',
              },
              {
                'mapping': 'objectives',
                'fieldName': 'Objetivos',
                'inputType': 'multiSelect',
                'options': ['sleep', 'close eyes', 'awake']
              }
          ],
        },
      ],
    }
    s.plt.input_form(
        menu_path='test/input-form', order=0,
        report_dataset_properties=report_dataset_properties
    )


def test_dynamic_and_conditional_input_form():
    print('test_dynamic_and_conditional_input_form')
    menu_path: str = 'test/input-dynamic-conditional'

    form_groups = {
        f'form group {i}': [{
            'mapping': 'country',
            'fieldName': f'Country {i}',
            'inputType': 'select',
            'options': ['España', 'Colombia']
          },
          {
            'dependsOn': f'Country {i}',
            'mapping': 'city',
            'fieldName': f'City {i}',
            'inputType': 'select',
            'options': {
                'España': ['Madrid', 'Barcelona'],
                'Colombia': ['Bogotá', 'Medellin']
            }
          }
        ] for i in range(4)}

    form_groups['Personal information'] = \
        [
            {
                'mapping': 'name',
                'fieldName': 'name',
                'inputType': 'text',
            },
            {
                'mapping': 'surname',
                'fieldName': 'surname',
                'inputType': 'text',
            },
            {
                'mapping': 'age',
                'fieldName': 'age',
                'inputType': 'number',
            },
            {
                'mapping': 'tel',
                'fieldName': 'phone',
                'inputType': 'tel',
            },
            {
                'mapping': 'gender',
                'fieldName': 'Gender',
                'inputType': 'radio',
                'options': ['Male', 'Female', 'No-binary', 'Undefined'],
            },
            {
                'mapping': 'email',
                'fieldName': 'email',
                'inputType': 'email',
            },
        ]

    form_groups['Other data'] = \
        [
            {
                'mapping': 'skills',
                'fieldName': 'Skills',
                'options': ['Backend', 'Frontend', 'UX/UI', 'Api Builder', 'DevOps'],
                'inputType': 'checkbox',
            },
            {
                'mapping': 'birthDay',
                'fieldName': 'Birthday',
                'inputType': 'date',
            },
            {
                'mapping': 'onCompany',
                'fieldName': 'Time on Shimoku',
                'inputType': 'dateRange',
            },
            {
                'mapping': 'hobbies',
                'fieldName': 'Hobbies',
                'inputType': 'select',
                'options': ['Make Strong Api', 'Sailing to Canarias', 'Send Abracitos'],
            },
            {
                'mapping': 'textField2',
                'fieldName': 'Test Text',
                'inputType': 'text',
            },
            {
                'mapping': 'objectives',
                'fieldName': 'Objetivos',
                'inputType': 'multiSelect',
                'options': ['sleep', 'close eyes', 'awake']
            }
        ]

    s.plt.generate_input_form_groups(
        menu_path=menu_path, order=0,
        form_groups=form_groups,
        dynamic_sequential_show=True
    )


def test_get_input_forms():
    print('test_get_input_forms')
    menu_path: str = 'test/input-form-to-get'
    report_dataset_properties = {
      'fields': [
        {
          'title': 'Personal information',
          'fields': [
            {
                'mapping': 'name',
                'fieldName': 'name',
                'inputType': 'text',
              },
              {
                'mapping': 'surname',
                'fieldName': 'surname',
                'inputType': 'text',
              },
            {
              'mapping': 'age',
              'fieldName': 'age',
              'inputType': 'number',
            },
            {
                'mapping': 'tel',
                'fieldName': 'phone',
                'inputType': 'tel',
              },
              {
                'mapping': 'gender',
                'fieldName': 'Gender',
                'inputType': 'radio',
                'options': ['Male', 'Female', 'No-binary', 'Undefined'],
              },
            {
                'mapping': 'email',
                'fieldName': 'email',
                'inputType': 'email',
              },

          ],
        },
        {
          'title': 'Other data',
          'fields': [
            {
              'mapping': 'skills',
              'fieldName': 'Skills',
              'options': ['Backend', 'Frontend', 'UX/UI', 'Api Builder', 'DevOps'],
              'inputType': 'checkbox',
            },
            {
                'mapping': 'birthDay',
                'fieldName': 'Birthday',
                'inputType': 'date',
              },
              {
                'mapping': 'onCompany',
                'fieldName': 'Time on Shimoku',
                'inputType': 'dateRange',
              },
              {
                'mapping': 'hobbies',
                'fieldName': 'Hobbies',
                'inputType': 'select',
                'options': ['Make Strong Api', 'Sailing to Canarias', 'Send Abracitos'],
              },
              {
                'mapping': 'textField2',
                'fieldName': 'Test Text',
                'inputType': 'text',
              },
          ],
        },
      ],
    }
    s.plt.input_form(
        menu_path=menu_path, order=0,
        report_dataset_properties=report_dataset_properties
    )
    rs: List[Dict] = s.plt.get_input_forms(menu_path)
    assert rs

def test_tabs():
    print("test_tabs")
    menu_path = "test-tabs"
    def _test_bentobox(tabs_index=("Deepness 0", "Bento box")):
        bentobox_id: Dict = {'bentoboxId': 'test20220101'}
        bentobox_data: Dict = {
            'bentoboxOrder': 0,
            'bentoboxSizeColumns': 8,
            'bentoboxSizeRows': 20,
        }
        bentobox_data.update(bentobox_id)

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
            order=0, rows_size=8, cols_size=12,
            value='value',
            header='title',
            footer='description',
            bentobox_data=bentobox_data,
            tabs_index=tabs_index
        )

        s.plt.indicator(
            data=data_,
            menu_path=menu_path,
            order=1, rows_size=8, cols_size=12,
            value='value',
            header='title',
            footer='description',
            bentobox_data=bentobox_id,
            tabs_index=tabs_index
        )

        data = [
            {'date': dt.date(2021, 1, 1), 'x': 5, 'y': 5},
            {'date': dt.date(2021, 1, 2), 'x': 6, 'y': 5},
            {'date': dt.date(2021, 1, 3), 'x': 4, 'y': 5},
            {'date': dt.date(2021, 1, 4), 'x': 7, 'y': 5},
            {'date': dt.date(2021, 1, 5), 'x': 3, 'y': 5},
        ]
        s.plt.bar(
            data=data,
            x='date', y=['x', 'y'],
            menu_path=menu_path,
            order=2, rows_size=14, cols_size=24,
            bentobox_data=bentobox_id,
            tabs_index=tabs_index
        )

    _test_bentobox()
    _test_bentobox(("Deepness 1", "Bento box"))
    tabs_index = ("Deepness 0", "line test")

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=0,
        tabs_index=tabs_index
    )

    s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        order=1,
        tabs_index=tabs_index
    )

    s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        x_axis_name='Date',
        y_axis_name=['Revenue'],
        # row=1, column=1,
        order=0, rows_size=2,
        cols_size=12,
        tabs_index=("Deepness 0", "Bar 1")
    )
    report_dataset_properties = {
        'fields': [
            {
                'title': 'Personal information',
                'fields': [
                    {
                        'mapping': 'name',
                        'fieldName': 'name',
                        'inputType': 'text',
                    },
                    {
                        'mapping': 'surname',
                        'fieldName': 'surname',
                        'inputType': 'text',
                    },
                    {
                        'mapping': 'age',
                        'fieldName': 'age',
                        'inputType': 'number',
                    },
                    {
                        'mapping': 'tel',
                        'fieldName': 'phone',
                        'inputType': 'tel',
                    },
                    {
                        'mapping': 'gender',
                        'fieldName': 'Gender',
                        'inputType': 'radio',
                        'options': ['Male', 'Female', 'No-binary', 'Undefined'],
                    },
                    {
                        'mapping': 'email',
                        'fieldName': 'email',
                        'inputType': 'email',
                    },

                ],
            },
            {
                'title': 'Other data',
                'fields': [
                    {
                        'mapping': 'skills',
                        'fieldName': 'Skills',
                        'options': ['Backend', 'Frontend', 'UX/UI', 'Api Builder', 'DevOps'],
                        'inputType': 'checkbox',
                    },
                    {
                        'mapping': 'birthDay',
                        'fieldName': 'Birthday',
                        'inputType': 'date',
                    },
                    {
                        'mapping': 'onCompany',
                        'fieldName': 'Time on Shimoku',
                        'inputType': 'dateRange',
                    },
                    {
                        'mapping': 'hobbies',
                        'fieldName': 'Hobbies',
                        'inputType': 'select',
                        'options': ['Make Strong Api', 'Sailing to Canarias', 'Send Abracitos'],
                    },
                    {
                        'mapping': 'textField2',
                        'fieldName': 'Test Text',
                        'inputType': 'text',
                    },
                    {
                        'mapping': 'objectives',
                        'fieldName': 'Objetivos',
                        'inputType': 'multiSelect',
                        'options': ['sleep', 'close eyes', 'awake']
                    },

                ],
            },
        ],
    }

    s.plt.input_form(
        menu_path=menu_path, order=0,
        report_dataset_properties=report_dataset_properties,
        tabs_index=("Deepness 0", "Input Form")
    )

    for i in range(5):
        s.plt.indicator(data={
            "description": "",
            "title": "",
            "value": "INDICATOR CHANGED!",
            "color": "warning"
        },
            menu_path=menu_path,
            order=0,
            value='value',
            header='title',
            footer='description',
            color='color',
            tabs_index=(f"Deepness {i}", "Indicators 1")
        )

        s.plt.indicator(data={
            "description": "",
            "title": "",
            "value": "INDICATOR CHANGED!",
            "color": "main"
        },
            menu_path=menu_path,
            order=0,
            value='value',
            header='title',
            footer='description',
            color='color',
            tabs_index=(f"Deepness {i}", "Indicators 2")
        )

    data_ = [{'date': dt.date(2021, 1, 1), 'x': 5, 'y': 5},
             {'date': dt.date(2021, 1, 2), 'x': 6, 'y': 5},
             {'date': dt.date(2021, 1, 3), 'x': 4, 'y': 5},
             {'date': dt.date(2021, 1, 4), 'x': 7, 'y': 5},
             {'date': dt.date(2021, 1, 5), 'x': 3, 'y': 5}]

    s.plt.bar(
        data=data_,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        x_axis_name='Date',
        y_axis_name=['Revenue'],
        # row=1, column=1,
        order=0, rows_size=2,
        cols_size=12,
        tabs_index=("Bar deep 1", "Bar 1")
    )
    s.plt.bar(
        data=data_,
        x='date', y=['y'],
        menu_path=menu_path,
        x_axis_name='Date',
        y_axis_name=['Revenue'],
        # row=1, column=1,
        order=2, rows_size=2,
        cols_size=12,
        tabs_index=("Bar deep 2", "Bar 1")
    )
    s.plt.line(
        data=data_,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        x_axis_name='Date',
        y_axis_name=['Revenue'],
        # row=1, column=1,
        order=0, rows_size=2,
        cols_size=12,
        tabs_index=("Bar deep 2", "Line 1")
    )
    s.plt.line(
        data=data_,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        x_axis_name='Date',
        y_axis_name=['Revenue'],
        # row=1, column=1,
        order=0, rows_size=2,
        cols_size=12,
        tabs_index=("Bar deep 2", "Line 2")
    )

    s.plt.insert_tabs_group_in_tab(menu_path=menu_path,
                                   parent_tab_index=("Bar deep 1", "Bar 1"),
                                   child_tabs_group="Bar deep 2")

    s.plt.insert_tabs_group_in_tab(menu_path=menu_path,
                                   parent_tab_index=("Deepness 0", "Bar 1"),
                                   child_tabs_group="Bar deep 1")

    for i in [4, 3, 2, 1]:
        s.plt.insert_tabs_group_in_tab(menu_path=menu_path,
                                       parent_tab_index=(f"Deepness {i - 1}", "Indicators 1"),
                                       child_tabs_group=(f"Deepness {i}")
                                       )

print(f'Start time {dt.datetime.now()}')
if delete_paths:
    s.plt.delete_path('test')

test_tabs()
test_line()
test_funnel()
test_tree()
test_get_input_forms()
test_delete_path()
test_append_data_to_trend_chart()
test_iframe()
test_html()
test_set_new_business()
test_table()
test_table_with_labels()
test_free_echarts()
test_input_form()
test_dynamic_and_conditional_input_form()
test_bentobox()
test_delete()
test_bar_with_filters()
test_set_apps_orders()
test_set_sub_path_orders()
test_zero_centered_barchart()
test_indicator()
test_indicator_one_dict()
test_alert_indicator()
test_stockline()
test_radar()
test_pie()
test_ux()
test_bar()
test_stacked_barchart()
test_stacked_horizontal_barchart()
test_stacked_area_chart()
test_shimoku_gauges()
test_doughnut()
test_rose()
test_ring_gauge()
test_sunburst()
test_treemap()
test_heatmap()
test_sankey()
test_horizontal_barchart()
test_predictive_line()
test_speed_gauge()
test_line()
test_scatter()


# TODO
# test_cohorts()
# test_themeriver()
# test_candlestick()
# test_scatter_with_confidence_area()
# test_bubble_chart()
# test_line_with_confidence_area()
print(f'End time {dt.datetime.now()}')
