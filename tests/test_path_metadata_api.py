""""""
from os import getenv
from typing import List, Dict

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
app_id: str = getenv('APP_ID')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
)


def test_check_if_path_exists():
    result: bool = (
        s.path.check_if_path_exists(
            business_id=business_id,
            app_id=app_id,
            path_name='test',
        )
    )
    assert result


def test_get_path_position():
    result: int = (
        s.path.get_path_position(
            business_id=business_id,
            app_id=app_id,
            path_name='test',
        )
    )
    assert result >= 0


def test_get_app_path_all_reports():
    reports: List[Dict] = (
        s.path.get_path_reports(
            business_id=business_id,
            app_id=app_id,
            path_name='test',
        )
    )
    assert reports


def test_change_path_name():
    old_path_name: str = 'test'
    new_path_name: str = 'test-renamed'

    result: bool = (
        s.path.test_check_if_path_exists(
            business_id=business_id,
            app_id=app_id,
            path=old_path_name,
        )
    )

    assert result

    result: bool = (
        s.path.test_check_if_path_exists(
            business_id=business_id,
            app_id=app_id,
            path=new_path_name,
        )
    )

    assert not result

    path_renamed: str = (
        s.path.change_path_name(
            business_id=business_id,
            app_id=app_id,
            old_path_name=old_path_name,
            new_path_name=new_path_name,
        )
    )
    assert path_renamed == new_path_name

    result: bool = (
        s.path.test_check_if_path_exists(
            business_id=business_id,
            app_id=app_id,
            path=old_path_name,
        )
    )

    assert not result

    # Revert the name change
    _ = (
        s.path.change_path_name(
            business_id=business_id,
            app_id=app_id,
            old_path_name=new_path_name,
            new_path_name=old_path_name,
        )
    )

    result: bool = (
        s.path.test_check_if_path_exists(
            business_id=business_id,
            app_id=app_id,
            path=old_path_name,
        )
    )

    assert result


def test_get_path_reports():
    reports: List[Dict] = (
        s.path.get_path_reports(
            business_id=business_id,
            app_id=app_id,
            path_name='test',
        )
    )
    assert reports


def test_change_path_position():
    position: int = (
        s.path.get_path_position(
            business_id=business_id,
            app_id=app_id,
            path_name='test',
        )
    )
    assert position == 0

    _ = (
        s.path.change_path_position(
            business_id=business_id,
            app_id=app_id,
            path_name='test',
            new_position=5,
        )
    )

    position: int = (
        s.path.get_path_position(
            business_id=business_id,
            app_id=app_id,
            path_name='test',
        )
    )
    assert position == 5

    # Revert the change

    _ = (
        s.path.change_path_position(
            business_id=business_id,
            app_id=app_id,
            path_name='test',
            new_position=0,
        )
    )

    position: int = (
        s.path.get_path_position(
            business_id=business_id,
            app_id=app_id,
            path_name='test',
        )
    )
    assert position == 0


# TODO pending to be tried
test_check_if_path_exists()
test_get_path_position()
test_get_app_path_all_reports()
test_change_path_name()
test_get_path_reports()
test_change_path_position()
