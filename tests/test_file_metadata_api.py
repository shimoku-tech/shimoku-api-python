""""""
from os import getenv
from typing import Dict, List
import unittest

import pandas as pd
import datetime as dt

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')


s = shimoku.Client(
    config={'access_token': api_key},
    universe_id=universe_id,
    environment=environment,
)


def test_create_file():
    data = {
        'a': [1, 2, 3],
        'b': [1, 4, 9],
    }
    df = pd.DataFrame(data)
    file_object = df.to_csv(index=False)
    filename = 'helloworld'
    file_metadata = {
        'name': filename,
        'fileName': ''.join(filename.split('_')),
        'contentType': 'text/csv',
    }

    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    file = s.file._create_file(
        business_id=business_id, app_id=app_id,
        file_metadata=file_metadata, file_object=file_object,
    )
    assert file


def test_get_files():
    test_create_file()

    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    files = s.file.get_files(business_id=business_id, app_id=app_id)
    assert files

    test_delete_file()


def test_get_file():
    test_create_file()

    filename = 'helloworld'

    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    files = s.file.get_files(business_id=business_id, app_id=app_id)
    for file in files:
        file_ = s.file._get_file(
            business_id=business_id,
            app_id=app_id,
            file_id=file['id'],
        )
        assert file_

    test_delete_file()


def test_delete_file():
    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    files = s.file.get_files(business_id=business_id, app_id=app_id)
    for file in files:
        s.file._delete_file(
            business_id=business_id,
            app_id=app_id,
            file_id=file['id'],
        )
    files = s.file.get_files(business_id=business_id, app_id=app_id)
    assert not files


def test_encode_file_name():
    file_name = 'helloworld'
    today = dt.date.today()
    new_file_name = s.file._encode_file_name(file_name=file_name, date=today)
    assert new_file_name == f'helloworld_date:{dt.date.today().isoformat()}'


def test_decode_file_name():
    file_name = f'helloworld_date:{dt.date.today().isoformat()}'
    new_file_name = s.file._decode_file_name(file_name)
    assert new_file_name == 'helloworld'


def test_get_file_date():
    today = dt.date.today()
    file_name = f'helloworld_date:{today.isoformat()}'
    date = s.file._get_file_date(file_name)
    assert date == today


def test_get_all_files_by_app_name():
    test_create_file()
    files: List[Dict] = s.file.get_all_files_by_app_name(
        business_id=business_id, app_name='test',
    )
    assert files
    test_delete_file()


def test_get_files_by_string_matching():
    test_create_file()

    files: List[Dict] = s.file._get_files_by_string_matching(
        business_id=business_id, string_match='hello',
    )
    assert files

    files: List[Dict] = s.file._get_files_by_string_matching(
        business_id=business_id, string_match='hello', app_name='test',
    )
    assert files

    files: List[Dict] = s.file._get_files_by_string_matching(
        business_id=business_id, string_match='fail', app_name='test',
    )
    assert not files

    files: List[Dict] = s.file._get_files_by_string_matching(
        business_id=business_id, string_match='hello', app_name='fail'
    )
    assert not files

    test_delete_file()


def test_get_file_by_name():
    test_create_file()

    file = s.file.get_file_by_name(
        business_id=business_id,
        app_name='test',
        file_name='helloworld',
        get_file_object=False,
    )
    assert file

    file = s.file.get_file_by_name(
        business_id=business_id,
        app_name='test',
        file_name='helloworld',
        get_file_object=True,
    )
    assert file

    test_delete_file()


def test_get_all_files_by_date():
    test_post_object()

    today = dt.date.today().isoformat()
    files: List[Dict] = s.file.get_files_by_date(
        business_id=business_id,
        date=today,
        app_name='test',
    )
    assert files

    tomorrow = today + dt.timedelta(1)
    files: List[Dict] = s.file.get_file_by_creation_date(
        business_id=business_id,
        date=tomorrow,
        app_name='test',
    )
    assert not files

    test_delete_file()


def test_get_all_files_by_creation_date():
    pass


def test_get_file_by_creation_date():
    pass


def test_get_last_created_target_file():
    pass


def test_get_all_files_by_date():
    file_name = 'helloworld'
    app_name = 'test'
    object_data = b''
    s.file.post_object(
        business_id=business_id,
        app_name=app_name,
        file_name=file_name,
        object_data=object_data
    )

    today = dt.date.today()
    files: List[Dict] = s.file.get_all_files_by_date(
        business_id=business_id,
        app_name='test',
        date=today,
    )
    assert files

    test_delete_file()


def test_get_file_by_date():
    today = dt.date.today()
    file_name = 'helloworld'
    app_name = 'test'
    object_data = b''
    s.file.post_object(
        business_id=business_id,
        app_name=app_name,
        file_name=file_name,
        object_data=object_data
    )

    file: Dict = s.file.get_file_by_date(
        business_id=business_id,
        date=today,
        file_name='helloworld',
        app_name='test',
    )

    assert file

    file_object: bytes = s.file.get_file_by_date(
        business_id=business_id,
        date=today,
        file_name='helloworld',
        app_name='test',
        get_file_object=True,
    )
    assert file_object == object_data

    tomorrow = today + dt.timedelta(1)
    file: Dict = s.file.get_file_by_date(
        business_id=business_id,
        date=tomorrow,
        app_name='test',
        file_name='helloworld',
    )
    assert not file


def test_get_file_with_max_date():
    file_name = 'helloworld'
    app_name = 'test'
    object_data = b''
    s.file.post_object(
        business_id=business_id,
        app_name=app_name,
        file_name=file_name,
        object_data=object_data
    )

    file = s.file.get_file_with_max_date(
        business_id=business_id,
        app_name='test',
        file_name='helloworld',
    )
    assert file['name'] == f'helloworld_date:{dt.date.today().isoformat()}'

    file_object = s.file.get_file_with_max_date(
        business_id=business_id,
        app_name='test',
        file_name='helloworld',
        get_file_object=True,
    )
    assert file_object == object_data

    test_delete_file()


def test_get_files_by_name_prefix():
    test_create_file()

    files: List[Dict] = s.file.get_files_by_name_prefix(
        business_id=business_id, name_prefix='hello', app_name='test',
    )
    assert files

    test_delete_file()


def test_delete_files_by_name_prefix():
    class MyTestCase(unittest.TestCase):
        def test_fake_business(self):
            with self.assertRaises(ValueError):
                s.file.get_file_by_name(
                    business_id=business_id,
                    file_name='helloworld',
                    app_name='test'
                )

    test_create_file()

    s.file.delete_files_by_name_prefix(
        business_id=business_id,
        file_name='helloworld',
        app_name='test',
    )

    t = MyTestCase()
    t.test_fake_business()


def test_replace_file_name():
    s.file._replace_file_name()


def test_post_object():
    file_name = 'helloworld'
    app_name = 'test'
    object_data = b''

    file = s.file.post_object(
        business_id=business_id,
        app_name=app_name,
        file_name=file_name,
        object_data=object_data
    )
    assert file
    assert file['name'] == f'{file_name}_date:{dt.date.today().isoformat()}'

    test_delete_file()


def test_get_object():
    file_name = 'helloworld'
    app_name = 'test'
    object_data = b''

    s.file.post_object(
        business_id=business_id,
        app_name=app_name,
        file_name=file_name,
        object_data=object_data
    )

    file = s.file.get_object(
        business_id=business_id,
        app_name=app_name,
        file_name=file_name,
    )
    assert file == object_data

    test_delete_file()


def test_post_dataframe():
    d = {'a': [1, 2, 3], 'b': [1, 4, 9]}
    df = pd.DataFrame(d)
    file: Dict = s.file.post_dataframe(
        business_id=business_id,
        app_name='test',
        file_name='df-test',
        df=df,
    )
    assert file

    test_delete_file()


def test_post_get_dataframe():
    file_name: str = 'df-test'
    d = {'a': [1, 2, 3], 'b': [1, 4, 9]}
    df_ = pd.DataFrame(d)
    file: Dict = s.file.post_dataframe(
        business_id=business_id,
        app_name='test',
        file_name=file_name,
        df=df_,
    )
    assert file

    df: pd.DataFrame = s.file.get_dataframe(
        business_id=business_id,
        app_name='test',
        file_name=file_name,
    )
    assert df.to_dict() == df_.to_dict()

    test_delete_file()


test_create_file()
test_delete_file()
test_get_file()
test_get_files()

test_encode_file_name()
test_decode_file_name()
test_get_file_date()

test_get_all_files_by_app_name()
test_get_files_by_string_matching()
test_get_files_by_name_prefix()

test_get_file_by_name()
test_delete_files_by_name_prefix()
test_post_object()
test_get_object()

test_get_all_files_by_date()
test_get_file_with_max_date()
test_get_file_by_date()

test_post_dataframe()
test_post_get_dataframe()

# TODO pending
# test_replace_file_name()

# TODO pending to have a createdAt
# test_get_all_files_by_creation_date()
# test_get_file_by_creation_date()
# test_get_last_created_target_file()
