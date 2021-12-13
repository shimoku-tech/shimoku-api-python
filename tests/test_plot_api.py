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


def test_bubble_chart():
    # s.plt.bubble_chart()
    raise NotImplementedError


def test_candlestick():
    # s.plt.candlestick()
    raise NotImplementedError


def test_funnel():
    # s.plt.funnel()
    raise NotImplementedError


def test_heatmap():
    # s.plt.heatmap()
    raise NotImplementedError


def test_gauge():
    # s.plt.gauge()
    raise NotImplementedError


def test_sunburst():
    # s.plt.sunburst()
    raise NotImplementedError


def test_tree():
    # s.plt.tree()
    raise NotImplementedError


def test_treemap():
    # s.plt.treemap()
    raise NotImplementedError


def test_indicator():
    # s.plt.indicator()
    raise NotImplementedError


def test_alert_indicator():
    # s.plt.alert_indicator()
    raise NotImplementedError


def test_line_with_confidence_area():
    # s.plt.line_with_confidence_area()
    raise NotImplementedError


def test_predictive_line():
    # s.plt.predictive_line()
    raise NotImplementedError


def test_radar():
    # s.plt.radar()
    raise NotImplementedError


test_bar()
test_line()
test_scatter()
test_stockline()
test_bubble_chart()
test_candlestick()
test_funnel()
test_heatmap()
test_gauge()
test_sunburst()
test_tree()
test_treemap()
test_indicator()
test_alert_indicator()
test_line_with_confidence_area()
test_predictive_line()
test_radar()
