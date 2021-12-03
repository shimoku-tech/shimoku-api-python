""""""
from os import getenv

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


def test_get_app_path_all_reports():
    result = s.path.get_app_path_all_reports(app_id=app_id, path='test')
    print(result)


def test_change_path_name():
    s.path.change_path_name(
        business_id
    )


def test_get_path_reports():
    s.path.get_path_reports()


def test_change_report_grid_position():
    s.path.change_report_grid_position()


def test_change_path_position():
    s.path.change_path_position()


# TODO pending to be tried
test_get_app_path_all_reports()
test_change_path_name()
test_get_path_reports()
test_change_report_grid_position()
test_change_path_position()
