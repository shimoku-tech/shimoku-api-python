""""""
from os import getenv
from typing import Dict, List
import unittest

import datetime as dt

import shimoku_api_python as shimoku
from shimoku_api_python.exceptions import ApiClientError


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
    r = s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/bar-test',
        row=1, column=1,
    )

    assert r

    s.report.delete_report(
        business_id=business_id,
        app_id=app_id,
        report_id=r['id']
    )


def test_line():
    r = s.plt.line(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/bar-test',
        row=1, column=1,
    )

    assert r

    s.report.delete_report(
        business_id=business_id,
        app_id=app_id,
        report_id=r['id']
    )


def test_stockline():
    r = s.plt.stockline(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/bar-test',
        row=1, column=1,
    )

    assert r

    s.report.delete_report(
        business_id=business_id,
        app_id=app_id,
        report_id=r['id']
    )


def test_scatter():
    r = s.plt.scatter(
        data=data,
        x='date', y=['x', 'y'],
        menu_path='test/bar-test',
        row=1, column=1,
    )

    assert r

    s.report.delete_report(
        business_id=business_id,
        app_id=app_id,
        report_id=r['id']
    )


test_bar()
test_line()
test_scatter()
test_stockline()
