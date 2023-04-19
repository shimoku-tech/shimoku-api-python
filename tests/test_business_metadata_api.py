""""""
from os import getenv
from typing import Dict, List
import json
import unittest

import shimoku_api_python as shimoku
from shimoku_api_python.exceptions import ApiClientError

from tenacity import RetryError

api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')
verbosity: str = getenv('VERBOSITY')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
    environment=environment,
    verbosity=verbosity,
)


def test_get_business():
    result = s.business.get_business(business_id)
    print(result)


def test_get_fake_business():
    class MyTestCase(unittest.TestCase):
        def test_fake_business(self):
            with self.assertRaises(RetryError):
                business_id_: str = 'this is a test'
                s.business.get_business(
                    business_id=business_id_,
                )

    t = MyTestCase()
    t.test_fake_business()


def test_create_and_delete_business():
    business: Dict = s.business.create_business(name='auto-test')
    business_id_: str = business['id']

    assert len(business_id_) > 0

    business_from_db: Dict = (
        s.business.get_business(
            business_id=business_id_,
        )
    )

    business_roles = s.business.get_roles(business_id=business_id_)

    assert len(business_roles) == 4
    resources = ['DATA', 'DATA_EXECUTION', 'USER_MANAGEMENT', 'BUSINESS_INFO']
    for role in business_roles:
        assert role['role'] == 'business_read'
        assert role['permission'] == 'READ'
        assert role['resource'] in resources
        assert role['target'] == 'GROUP'
        resources.remove(role['resource'])

    assert {
        k: v
        for k, v in business_from_db.items()
        if k in [
            'id', 'name',
            'universe', '__typename',
        ]
    } == {
        k: v
        for k, v in business.items()
        if k in [
            'id', 'name',
            'universe', '__typename',
        ]
    }
    del business_from_db

    s.business.delete_business(business_id=business_id_)

    class MyBusinessDeletedCase(unittest.TestCase):
        def test_business_deleted(self):
            with self.assertRaises(RetryError):
                s.business.get_business(
                    business_id=business_id_,
                )

    t = MyBusinessDeletedCase()
    t.test_business_deleted()


def test_theme_customization():
    s.business.update_business_theme(
        business_id=business_id,
        theme={},
    )
    business: Dict = (
        s.business.get_business(business_id)
    )

    assert business['theme'] == '{}'

    theme = {
        "palette": {
            "primary": {
                "main": "#0f530b",
            },
        },
        "typography": {
            "h1": {
                "fontSize": "60px",
            },
        },
        "custom": {
            "radius": {
                "xs": "0px",
                "s": "0px",
                "m": "0px",
                "l": "0px",
                "xl": "0px"
            },
            "logo": "https://flaxandkale.com/img/logo-flaxandkale-black.png",
        }
    }

    s.business.update_business_theme(
        business_id=business_id,
        theme=theme,
    )

    business: Dict = (
        s.business.get_business(business_id)
    )

    assert json.loads(business['theme']) == theme


def test_update_business():
    business_original: Dict = (
        s.business.get_business(business_id)
    )
    business_name: str = business_original['name']
    new_business_name: str = f'{business_name}_changed'

    new_business: Dict = (
        s.business.update_business(
            business_id=business_id,
            business_data={'name': new_business_name},
        )
    )

    business_changed: Dict = s.business.get_business(business_id)
    assert {
        k: v
        for k, v in business_changed.items()
        if k in [
            'id', 'name',
            'universe', '__typename',
        ]
    } == {
        k: v
        for k, v in new_business.items()
        if k in [
            'id', 'name',
            'universe', '__typename',
        ]
    }
    assert new_business_name == business_changed['name']

    # Restore previous name
    _ = (
        s.business.update_business(
            business_id=business_id,
            business_data={'name': business_name},
        )
    )
    business_restored: Dict = s.business.get_business(business_id)
    assert business_name == business_restored['name']


def test_rename_business():
    business_original: Dict = (
        s.business.get_business(business_id)
    )
    business_name: str = business_original['name']
    new_business_name: str = f'{business_name}_changed'

    new_business: Dict = (
        s.business.rename_business(
            business_id=business_id,
            new_name=new_business_name,
        )
    )

    business_changed: Dict = s.business.get_business(business_id)
    assert {
        k: v
        for k, v in business_changed.items()
        if k in [
            'id', 'name',
            'universe', '__typename',
        ]
    } == {
        k: v
        for k, v in new_business.items()
        if k in [
            'id', 'name',
            'universe', '__typename',
        ]
    }
    assert new_business_name == business_changed['name']

    # Restore previous name
    _ = (
        s.business.rename_business(
            business_id=business_id,
            new_name=business_name,
        )
    )
    business_restored: Dict = s.business.get_business(business_id)
    assert business_name == business_restored['name']


def test_get_business_apps():
    apps: List[Dict] = s.business.get_business_apps(business_id)
    assert apps


test_get_business()
test_get_fake_business()
test_create_and_delete_business()
test_theme_customization()
test_update_business()
test_rename_business()
test_get_business_apps()
