"""
To create a report

r = {
    'business_id': business_id,
    'app_id': app_id,
    'report_metadata': {
        'title': 'test',
        'order': 0,
        'grid': '1, 1',
        'path': 'test',
        'reportType': 'LINECHART',
        'chartData': '[{"name": "Matcha Latte", "value": 78}, {"name": "Milk Tea", "value": 17}, {"name": "Cheese Cocoa", "value": 18}, {"name": "Walnut Brownie", "value": 9}]'
    }
}
s.report.create_report(**r)

"""
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
report_id: str = getenv('REPORT_ID')
environment: str = getenv('ENVIRONMENT')
report_element: Dict[str, str] = dict(
    business_id=business_id,
    app_id=app_id,
    report_id=report_id
)


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
    environment=environment,
)


def test_get_report():
    report: Dict = s.report.get_report(**report_element)
    assert report


def test_update_report():
    """Set the updatedAt field of an report to '2000-01-01'
    Then revert the updatedAt to its original value
    """
    report: Dict = s.report.get_report(**report_element)
    old_val: str = report['reportType']

    val: str = 'BARCHART'
    assert old_val != val

    report_data: Dict = {'reportType': val}
    s.report.update_report(
        report_metadata=report_data,
        **report_element,
    )

    report_updated: Dict = s.report.get_report(**report_element)

    assert report_updated['reportType'] == val

    #########
    # Revert the change
    #########

    report_data: Dict = {'reportType': old_val}
    s.report.update_report(
        report_metadata=report_data,
        **report_element,
    )

    report_updated: Dict = s.report.get_report(**report_element)

    assert report_updated['reportType'] == old_val


def test_create_and_delete_report():
    report_metadata = {
        'title': 'test',
        'order': 0,
        'grid': '1, 1',
        'path': 'test',
        'reportType': 'LINECHART',
    }
    new_report: Dict = (
        s.report.create_report(
            business_id=business_id,
            app_id=app_id,
            report_metadata=report_metadata,
        )
    )
    new_report_id: str = new_report['id']

    report: Dict = s.report.get_report(
        business_id=business_id,
        app_id=app_id,
        report_id=new_report_id,
    )

    assert new_report == {
        k: v
        for k, v in report.items()
        if k in [
            'id', 'appId', 'reportDataSets',
            'path', 'pathOrder', 'grid',
            'createdAt', 'order', 'reportType',
            'dataFields', 'title', 'sizeRows',
            'sizeColumns', 'sizePadding', 'smartFilters',
            'subscribe', 'updatedAt', 'bentobox',
            'hidePath', 'isDisabled',
            'properties', '__typename',
        ]
    }

    s.report.delete_report(
        business_id=business_id,
        app_id=app_id,
        report_id=new_report_id,
    )

    # Check it does not exists anymore
    class MyTestCase(unittest.TestCase):
        def check_report_not_exists(self):
            with self.assertRaises(ApiClientError):
                s.report.get_report(
                    business_id=business_id,
                    app_id=app_id,
                    report_id=new_report_id,
                )

    t = MyTestCase()
    t.check_report_not_exists()


def test_get_report_data():
    data: List[Dict] = s.report.get_report_data(**report_element)
    assert data
    assert len(data[0]) > 0


def test_get_reports_in_same_app():
    reports: List[str] = s.report.get_reports_in_same_app(**report_element)
    assert reports
    assert len(reports) > 1


def test_get_reports_in_same_path():
    reports: List[str] = s.report.get_reports_in_same_path(**report_element)
    assert reports
    assert len(reports) > 1


def test_get_report_last_update():
    last_update: dt.datetime = s.report.get_report_last_update(**report_element)


def test_get_report_by_title():
    title: str = 'test'
    reports: Dict = (
        s.report.get_reports_by_title(
            business_id=business_id,
            app_id=app_id,
            title=title,
        )
    )
    assert reports
    assert all([r['title'] == title for r in reports])


def test_get_report_by_path():
    path: str = 'test'
    reports: Dict = (
        s.report.get_reports_by_path(
            business_id=business_id,
            app_id=app_id,
            path=path,
        )
    )
    assert reports
    assert all([r['path'] == path for r in reports])


def test_get_report_by_chart_type():
    report_type: str = 'LINECHART'
    reports: List[Dict] = (
        s.report.get_reports_by_chart_type(
            business_id=business_id,
            app_id=app_id,
            chart_type=report_type,
        )
    )
    assert reports
    assert all([r['reportType'] == report_type for r in reports])


def test_get_report_by_grid_position():
    row: int = 1
    column: int = 1
    grid = f'{row}, {column}'
    reports: List[Dict] = (
        s.report.get_reports_by_grid_position(
            business_id=business_id,
            app_id=app_id,
            row=row, column=column,
        )
    )
    assert reports
    assert all([r['grid'].strip() == grid for r in reports])


# TODO
def test_change_report_grid_position():
    # s.report.change_report_grid_position()
    raise NotImplementedError


def test_fetch_filter_report():
    # s.report.fetch_filter_report()
    raise NotImplementedError


def test_add_report_to_filter():
    # s.report.add_report_to_filter()
    raise NotImplementedError


def test_set_filter_to_reports():
    # s.report.set_filter_to_reports()
    raise NotImplementedError


def test_remove_filter_for_report():
    # s.report.remove_filter_for_report()
    raise NotImplementedError


def test_hide_report():
    s.report.hide_report(**report_element)
    assert s.report.get_report(**report_element)['isDisabled']


def test_unhide_report():
    s.report.unhide_report(**report_element)
    assert not s.report.get_report(**report_element)['isDisabled']


test_get_report()
test_create_and_delete_report()
test_update_report()
test_get_reports_in_same_path()
test_get_report_data()

test_get_report_by_title()
test_get_report_by_path()
test_get_report_by_chart_type()
test_get_report_by_grid_position()
test_hide_report()
test_unhide_report()

# TODO
"""
test_change_report_grid_position()
test_get_filter_report()
test_add_report_to_filter()
test_remove_filter_for_report()
test_set_filter_to_reports()
test_fetch_filter_report()
"""
