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


def test_get_app():
    app: Dict = s.app.get_app(
        business_id=business_id,
        app_id=app_id,
    )
    assert app


def test_get_fake_app():
    class MyTestCase(unittest.TestCase):
        def test_fake_app(self):
            with self.assertRaises(ApiClientError):
                app_id_: str = 'this is a test'
                s.app.get_app(
                    business_id=business_id,
                    app_id=app_id_,
                )

    t = MyTestCase()
    t.test_fake_app()


def test_update_app():
    """Set the updatedAt field of an App to '2000-01-01'
    Then revert the updatedAt to its original value
    """
    var: str = 'trialDays'
    app: Dict = s.app.get_app(**app_element)
    old_val: str = app.get(var)

    val: str = 10
    app_data: Dict = {var: val}
    x: Dict = s.app.update_app(
        app_data=app_data, **app_element
    )

    app_updated: Dict = s.app.get_app(**app_element)

    assert x == app_updated
    assert app_updated[var] == val

    #########
    # Revert the change
    #########

    app_data: Dict = {var: old_val}
    new_x: Dict = s.app.update_app(
        app_data=app_data, **app_element,
    )

    app_updated: Dict = s.app.get_app(**app_element)

    assert new_x == app_updated
    assert app_updated[var] == old_val


def test_create_and_delete_app():
    test_app_type_id: str = getenv('APP_TYPE_TEST')

    if test_app_type_id is None:
        raise ValueError('You must provide a test_app_type_id')

    app: Dict = (
        s.app.create_app(
            business_id=business_id,
            app_type_id=test_app_type_id,
        )
    )
    app_id_: str = app['id']

    assert len(app_id_) > 0

    app: Dict = s.app.get_app(**app_element)

    assert app['createdAt'] == dt.date.today()

    result: Dict = (
        s.app.delete_app(
            business_id=business_id,
            app_id=app_id_,
        )
    )

    assert result


def test_create_and_delete_app_without_apptype():
    app: Dict = (
        s.app.create_app(
            business_id=business_id,
            app_type_id={},
            app_type_data={'name': 'new-apptype-test'}
        )
    )
    app_id_: str = app['id']
    app_type_id_: str = app['appTypeId']  # TODO check the key name

    assert len(app_id_) > 0
    assert len(app_type_id_) > 0

    app: Dict = s.app.get_app(**app_element)

    assert app['createdAt'] == dt.date.today()

    app_type: Dict = s.app_type.get_app_type(app_type_id=app_type_id_)

    assert app_type

    result: Dict = (
        s.app.delete_app(
            business_id=business_id,
            app_id=app_id_,
        )
    )

    assert result

    class MyTestCase(unittest.TestCase):
        def test_app_not_exists(self):
            with self.assertRaises(ApiClientError):
                s.app.get_app(
                    business_id=business_id,
                    app_id=app_id_,
                )

    t = MyTestCase()
    t.test_app_not_exists()

    _ = (
        s.app_type.delete_app_type(
            app_type_id=app_type_id_,
        )
    )

    class MyTestCase(unittest.TestCase):
        def test_apptype_not_exists(self):
            with self.assertRaises(ApiClientError):
                s.app_type.get_app_type(app_type_id=app_type_id_)

    t = MyTestCase()
    t.test_apptype_not_exists()


def test_get_app_reports():
    reports: List[Dict] = s.app.get_app_reports(**app_element)
    assert reports
    assert reports[0]


def test_get_app_report_ids():
    report_ids: List[str] = s.app.get_app_report_ids(**app_element)
    assert report_ids
    assert len(report_ids[0]) > 0
    assert isinstance(report_ids[0], str)


def test_get_app_path_names():
    path_names: List[str] = s.app.get_app_path_names(**app_element)
    assert path_names


def test_get_app_by_name():
    app_name: str = ''  # TODO
    app: Dict = s.app.get_app_by_name(**app_element)
    assert isinstance(app, dict)
    assert len(app) > 0


def test_rename_app():
    new_app_name: str = 'test'
    app: Dict = s.app.rename_app(
        new_app_name=new_app_name,
        **app_element,
    )
    old_val: str = app.get(var)

    val: str = 10
    app_data: Dict = {var: val}
    x: Dict = s.app.update_app(
        business_id=business_id,
        app_id=app_id,
        app_data=app_data
    )

    app_updated: Dict = s.app.get_app(**app_element)

    assert x == app_updated
    assert app_updated[var] == val

    #########
    # Revert the change
    #########

    app_data: Dict = {var: old_val}
    new_x: Dict = s.app.update_app(
        app_data=app_data, **app_element
    )

    app_updated: Dict = s.app.get_app(**app_element)

    assert new_x == app_updated
    assert app_updated[var] == old_val


def test_hide_and_show_title():
    col_var: str = ''  # TODO 'titleStatus' ??

    app: Dict = s.app.get_app(**app_element)
    title_status: bool = app[col_var]

    if title_status:
        s.app.hide_title(**app_element)
        app_updated: Dict = s.app.get_app(**app_element)
        assert not app_updated[col_var]

        s.app.show_title(**app_element)
        app_updated: Dict = s.app.get_app(**app_element)
        assert app_updated[col_var]
    else:
        s.app.show_title(**app_element)
        app_updated: Dict = s.app.get_app(**app_element)
        assert app_updated[col_var]

        s.app.hide_title(**app_element)
        app_updated: Dict = s.app.get_app(**app_element)
        assert not app_updated[col_var]


def test_get_app_by_type():
    app_type: str = ''  # TODO
    app: Dict = s.app.get_app_by_type(
        business_id=business_id,
        app_type=app_type,
    )
    assert app
    assert isinstance(app, dict)


def test_has_app_report():
    has_reports: bool = s.app.has_app_report(**app_element)
    assert has_reports


test_get_app()
test_get_fake_app()
# test_update_app()
# TODO pending:
# test_create_and_delete_app()
# test_create_and_delete_app_without_apptype()
# test_get_app_reports()
# test_get_app_report_ids()
# test_get_app_path_names()
# TODO pending:
test_get_app_by_name()
test_update_app()
test_get_app_by_type()
test_has_app_report()
