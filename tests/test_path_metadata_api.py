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


def test_set_paths_position():
    paths: List[str] = s.path._get_app_path_names(
        business_id=business_id,
        app_id=app_id,
    )
    reports: List[Dict] = s.path._get_app_reports(
        business_id=business_id,
        app_id=app_id,
    )

    # Example: {'catalog_path': 1, 'map_path': 2, ...}
    new_path_order: Dict[str, int] = {
        path: index
        for index, path in enumerate(paths)
    }

    s.path.set_paths_position(
        business_id=business_id,
        app_id=app_id,
        paths_position=new_path_order,
    )

    reports_new: List[Dict] = s.path._get_app_reports(
        business_id=business_id,
        app_id=app_id,
    )

    # This is to check that all reports from a path have the order that we have set
    assert all([
        report_new['order'] == new_path_order[report_new['path']]
        for report_new in reports_new
    ])

    # Restore previous version
    for report in reports:
        s.path._update_report(
            business_id=business_id,
            app_id=app_id,
            report_metadata={'order': report['order']}
        )

    reports_restored: List[Dict] = s.path._get_app_reports(
        business_id=business_id,
        app_id=app_id,
    )

    assert report == reports_restored


def test_fix_path_grid():
    # s.path.fix_path_grid()
    raise NotImplementedError


test_check_if_path_exists()
test_get_path_position()
test_get_app_path_all_reports()
test_change_path_name()
test_get_path_reports()
test_change_path_position()
test_set_paths_position()
test_fix_path_grid()
