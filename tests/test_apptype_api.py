""""""

from os import getenv
from typing import Dict
import unittest
from tenacity import RetryError

import shimoku_api_python as shimoku
from shimoku_api_python.exceptions import ApiClientError
import asyncio


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
app_type_id: str = getenv('APP_TYPE_ID')
environment: str = getenv('ENVIRONMENT')
verbosity: str = getenv('VERBOSITY')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
    environment=environment,
    business_id=business_id,
    verbosity=verbosity
)

#TODO dont use asyncio.run solve it in the class

def test_get_app_type():
    app_type: Dict = (
        asyncio.run(s.app_type.get_app_type(
            app_type_id=app_type_id,
        ))
    )
    assert app_type


def test_cannot_create_duplicated_app_type():
    class MyTestCase(unittest.TestCase):
        def check_app_type_not_exists(self):
            with self.assertRaises(ValueError):
                asyncio.run(s.app_type.create_app_type(name='test'))

    t = MyTestCase()
    t.check_app_type_not_exists()


def test_create_and_delete_app_type():
    app_type_new: Dict = asyncio.run(s.app_type.create_app_type(name='new-test'))
    app_type_id_: str = app_type_new['id']

    app_type_: Dict = asyncio.run(s.app_type.get_app_type(app_type_id=app_type_id_))
    assert app_type_new == {
        k: v
        for k, v in app_type_.items()
        if k in [
            'id', 'key', 'name', 'universe',
            'normalizedName', '__typename',
        ]
    }

    asyncio.run(s.app_type.delete_app_type(app_type_id=app_type_id_))

    # Check it does not exists anymore
    class MyTestCase(unittest.TestCase):
        def check_app_type_not_exists(self):
            with self.assertRaises(RetryError):
                asyncio.run(s.app_type.get_app_type(
                    app_type_id=app_type_id_,
                ))

    t = MyTestCase()
    t.check_app_type_not_exists()


def test_update_app_type():
    target_col_name: str = 'name'
    app_type: Dict = asyncio.run(s.app_type.get_app_type(app_type_id=app_type_id))
    name: str = app_type[target_col_name]

    new_name: str = f'{name}_test'
    data = {'name': new_name}
    app_type_updated: Dict = (
        asyncio.run(s.app_type.update_app_type(
            app_type_id=app_type_id,
            app_type_metadata=data,
        ))
    )
    assert (
        {
            k: v
            for k, v in app_type.items()
            if k in [
                'id', 'key', 'universe',  # name excluded
                'normalizedName', '__typename',
            ]
        } == {
            k: v
            for k, v in app_type_updated.items()
            if k in [
                'id', 'key', 'universe',  # name excluded
                'normalizedName', '__typename',
            ]
        }
    )
    assert app_type_updated[target_col_name] == new_name
    app_type_updated_: Dict = asyncio.run(s.app_type.get_app_type(app_type_id=app_type_id))
    assert app_type_updated_[target_col_name] == new_name
    assert app_type_updated == {
        k: v
        for k, v in app_type_updated_.items()
        if k in [
            'id', 'key', 'name', 'universe',
            'normalizedName', '__typename',
        ]
    }

    # Undo change
    data = {'name': name}
    app_type_restored: Dict = (
        asyncio.run(s.app_type.update_app_type(
            app_type_id=app_type_id,
            app_type_metadata=data,
        ))
    )
    assert {
        k: v
        for k, v in app_type_restored.items()
        if k in [
            'id', 'key', 'name', 'universe',
            'normalizedName', '__typename',
        ]
    } == {
        k: v
        for k, v in app_type.items()
        if k in [
            'id', 'key', 'name', 'universe',
            'normalizedName', '__typename',
        ]
    }


def test_rename_apps_types():
    target_col_name: str = 'name'
    app_type: Dict = asyncio.run(s.app_type.get_app_type(app_type_id=app_type_id))
    name: str = app_type[target_col_name]

    new_name: str = f'{name}_test'
    app_type_updated: Dict = (
        asyncio.run(s.app_type.rename_apps_types(
            app_type_id=app_type_id,
            new_name=new_name,
        ))
    )
    assert (
        {
            k: v
            for k, v in app_type.items()
            if k in [
                'id', 'key', 'universe',  # name excluded
                'normalizedName', '__typename',
            ]
        } == {
            k: v
            for k, v in app_type_updated.items()
            if k in [
                'id', 'key', 'universe',  # name excluded
                'normalizedName', '__typename',
            ]
        }
    )
    assert app_type_updated[target_col_name] == new_name
    app_type_updated_: Dict = asyncio.run(s.app_type.get_app_type(app_type_id=app_type_id))
    assert app_type_updated_[target_col_name] == new_name
    assert app_type_updated == {
        k: v
        for k, v in app_type_updated_.items()
        if k in [
            'id', 'key', 'name', 'universe',
            'normalizedName', '__typename',
        ]
    }

    # Undo change
    app_type_restored: Dict = (
        asyncio.run(s.app_type.rename_apps_types(
            app_type_id=app_type_id,
            new_name=name,
        ))
    )
    assert {
        k: v
        for k, v in app_type_restored.items()
        if k in [
            'id', 'key', 'name', 'universe',
            'normalizedName', '__typename',
        ]
    } == {
        k: v
        for k, v in app_type.items()
        if k in [
            'id', 'key', 'name', 'universe',
            'normalizedName', '__typename',
        ]
    }


def test_rename_app_type_by_old_name():
    app_type: Dict = asyncio.run(s.app_type.create_app_type(name='testrenameapptypebyoldname'))
    new_name: str = 'testrenameapptypebyoldname2'
    new_app_type: Dict = asyncio.run(s.app_type.rename_app_type_by_old_name(
        old_name='testrenameapptypebyoldname',
        new_name=new_name,
    ))
    app_types = s.universe.get_universe_app_types()
    assert [
        app_type_
        for app_type_ in app_types
        if app_type_['name'] == new_name
    ]
    asyncio.run(s.app_type.delete_app_type(app_type_id=app_type['id']))


test_get_app_type()
# test_cannot_create_duplicated_app_type()
test_create_and_delete_app_type()
test_update_app_type()
test_rename_apps_types()
test_rename_app_type_by_old_name()
