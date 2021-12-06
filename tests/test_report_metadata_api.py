""""""
from os import getenv
from typing import Dict, List

import datetime as dt

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
app_id: str = getenv('APP_ID')
report_id: str = getenv('REPORT_ID')
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
)


def test_get_report():
    report: Dict = s.report.get_report(**report_element)
    assert report


def test_update_report():
    """Set the updatedAt field of an report to '2000-01-01'
    Then revert the updatedAt to its original value
    """
    report: Dict = s.report.get_report(**report_element)
    old_val: str = report['updatedAt']

    val: str = '2000-01-01'
    report_data: Dict = {
        'updatedAt': val
    }
    s.report.update_report(
        report_metadata=report_data,
        **report_element,
    )

    report_updated: Dict = s.report.get_report(**report_element)

    assert report_updated['updatedAt'] == val

    #########
    # Revert the change
    #########

    report_data: Dict = {
        'updatedAt': old_val
    }
    s.report.update_report(
        report_metadata=report_data,
        **report_element,
    )

    report_updated: Dict = s.report.get_report(**report_element)

    assert report_updated['updatedAt'] == old_val


def test_create_and_delete_report():
    new_report_id: str = (
        s.report.create_report(
            business_id=business_id,
            app_id=app_id,
        )
    )

    report: Dict = s.report.get_report(
        business_id=business_id,
        app_id=app_id,
        report_id=new_report_id,
    )

    assert report['createdAt'] == dt.date.today()

    result: Dict = s.report.delete_report(
        business_id=business_id,
        app_id=app_id,
        report_id=new_report_id,
    )

    assert result

    result: Dict = s.report.get_report(
        business_id=business_id,
        app_id=app_id,
        report_id=new_report_id,
    )

    assert not result


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
    title: str = ''  # TODO
    report: Dict = (
        s.report.get_report_by_title(
            title=title,
            **report_element,
        )
    )
    assert report
    assert report['title'] == title


def test_get_report_by_path():
    path: str = ''  # TODO
    report: Dict = (
        s.report.get_report_by_path(
            path=path,
            **report_element,
        )
    )
    assert report
    assert report['path'] == path


def test_get_report_by_external_id():
    external_id: str = ''  # TODO
    report: Dict = (
        s.report.get_report_by_external_id(
            external_id=external_id,
            **report_element,
        )
    )
    assert report
    assert report['codeETLId'] == external_id


def test_get_report_by_chart_type():
    chart_type: str = ''  # TODO
    report: Dict = (
        s.report.get_report_by_chart_type(
            chart_type=chart_type,
            **report_element,
        )
    )
    assert report
    assert report['chartType'] == chart_type


def test_get_report_by_grid_position():
    row: int = 1
    column: int = 1
    report: Dict = (
        s.report.get_report_by_grid_position(
            row=row, column=column,
            **report_element,
        )
    )
    assert report
    assert report['grid'] == f'{row}, {column}'


# TODO
def test_change_report_grid_position():
    s.report.change_report_grid_position()


def test_get_filter_report():
    # s.report.get_filter_report()
    raise NotImplementedError


def test_get_filter_reports():
    # s.report.get_filter_reports()
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


test_get_report()
# TODO all below pending to be tried
test_update_report()
test_create_and_delete_report()
test_get_report_data()

# TODO pending
test_get_reports_in_same_app()
test_get_reports_in_same_path()

test_get_report_by_title()
test_get_report_by_path()
test_get_report_by_external_id()
test_get_report_by_chart_type()
test_get_report_by_grid_position()
test_change_report_grid_position()

test_get_filter_report()
test_get_filter_reports()
test_add_report_to_filter()
test_remove_filter_for_report()
test_set_filter_to_reports()
test_fetch_filter_report()
