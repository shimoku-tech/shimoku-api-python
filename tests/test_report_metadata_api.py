""""""
from os import getenv
from typing import Dict, List

import datetime as dt

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
business_id: str = getenv('BUSINESS_ID')
app_id: str = getenv('APP_ID')
report_id: str = getenv('REPORT_ID')


config = {
    'access_token': api_key
}

s = shimoku.Client(config)


def test_get_report():
    report: Dict = s.report.get_report(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
    )
    assert report


def test_update_report():
    """Set the updatedAt field of an report to '2000-01-01'
    Then revert the updatedAt to its original value
    """
    report: Dict = s.report.get_report(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
    )
    old_val: str = report['updatedAt']

    val: str = '2000-01-01'
    report_data: Dict = {
        'updatedAt': val
    }
    s.report.update_report(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
        report_data=report_data,
    )

    report_updated: Dict = (
        s.report.get_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )

    assert report_updated['updatedAt'] == val

    #########
    # Revert the change
    #########

    report_data: Dict = {
        'updatedAt': old_val
    }
    s.report.update_report(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
        report_data=report_data
    )

    report_updated: Dict = (
        s.report.get_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )

    assert report_updated['updatedAt'] == old_val


# TODO
def test_create_and_delete_report():
    raise NotImplementedError


def test_get_report_data():
    data: List[Dict] = (
        s.report.get_report_data(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )
    assert data
    assert len(data[0]) > 0


def test_get_reports_in_same_app():
    reports: List[str] = (
        s.report.get_reports_in_same_app(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )


def test_get_reports_in_same_path():
    reports: List[str] = (
        s.report.get_reports_in_same_path(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )


def test_get_report_by_name():
    report: Dict = s.report.get_report_by_name(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
    )


test_get_report()
test_update_report()
test_create_and_delete_report()
