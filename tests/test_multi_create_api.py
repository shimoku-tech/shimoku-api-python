""""""
from os import getenv

import shimoku_api_python as shimoku

api_key: str = getenv('API_TOKEN')
base_url: str = getenv('BASE_URL')
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


def test_create_business_and_app():
    # TODO it must create and delete
    # s.wildcards.create_business_and_app
    raise NotImplementedError


def test_create_app_type_and_app():
    # TODO it must create and delete
    # s.wildcards.create_app_type_and_app
    raise NotImplementedError


def test_create_app_and_report():
    # TODO it must create and delete
    # s.wildcards.create_app_and_report
    raise NotImplementedError


def test_create_business_app_and_report():
    # TODO it must create and delete
    # s.wildcards.create_business_app_and_report
    raise NotImplementedError


def test_create_business_app_type_app_and_report():
    # TODO it must create and delete
    # s.wildcards.create_business_app_type_app_and_report
    raise NotImplementedError


test_create_business_and_app()
test_create_app_type_and_app()
test_create_app_and_report()
test_create_business_app_and_report()
test_create_business_app_type_app_and_report()
