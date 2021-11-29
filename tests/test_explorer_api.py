""""""
from os import getenv

import shimoku_api_python as shimoku

api_key: str = getenv('API_TOKEN')
business_id: str = getenv('BUSINESS_ID')
app_id: str = getenv('APP_ID')
base_url: str = getenv('BASE_URL')

config = {
    'access_token': api_key
}

s = shimoku.Client(config)


# TODO pending https://trello.com/c/18GLgLoQ
def test_get_business():
    result = s.explorer.get_business(business_id)
    assert result.status_code == 200
    print(result)


def test_get_app_id():
    result = s.explorer.get_app(
        business_id=business_id, app_id=app_id
    )
    assert result.status_code == 200
    print(result)


def test_get_report(report_id):
    result = s.explorer.get_report(
        business_id=business_id, app_id=app_id, report_id=report_id,
    )
    assert result.status_code == 200
    print(result)


# TODO pending https://trello.com/c/REZNlpeG/
def test_get_business_id_by_app():
    result = s.explorer.get_business_id_by_app(app_id)
    print(result)


# TODO pending https://trello.com/c/CNhYPEDe/
def test_create_business():
    result = s.explorer.create_business(
        owner_id=,
        name='business-test',
    )
    assert result.status_code == 200
    print(result)


# TODO pending https://trello.com/c/CNhYPEDe/
def test_create_app():
    result = s.explorer.create_app(business_id)
    assert result.status_code == 200
    print(result)


# TODO pending https://trello.com/c/CNhYPEDe/
def test_create_report():
    result = s.explorer.create_report()
    assert result.status_code == 200
    print(result)


# test_get_business()
# test_get_app()
# test_get_report(report_id='')
test_get_business_id_by_app()

# test_create_business()
# test_create_app()
# test_create_report()

