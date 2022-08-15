""""""
from os import getenv
from typing import Dict, List
import unittest

import pandas as pd
import shimoku_api_python as shimoku
from shimoku_api_python.exceptions import ApiClientError


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
app_id: str = getenv('APP_ID')
app_type_id: str = getenv('APP_TYPE_ID')
environment: str = getenv('ENVIRONMENT')
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
    environment=environment,
)


def test_create_file():
    data = {
        'a': [1, 2, 3],
        'b': [1, 4, 9],
    }
    df = pd.DataFrame(data)
    file_object = df.to_csv(index=False)
    filename = 'test_file_metadata_api'
    file_metadata = {
        'name': filename,
        'fileName': ''.join(filename.split('_')),
        'contentType': 'text/csv',
    }

    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    s.file.create_file(
        business_id=business_id, app_id=app_id,
        file_metadata=file_metadata, file_object=file_object,
    )


def test_get_files():
    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    files = s.file.get_files(business_id=business_id, app_id=app_id)
    assert files


def test_get_file():
    filename = 'test_file_metadata_api'
    filename_normalized = ''.join(filename.split('_'))

    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    files = s.file.get_files(business_id=business_id, app_id=app_id)
    for file in files:
        file_ = s.file.get_file(
            business_id=business_id,
            app_id=app_id,
            file_id=file['id'],
        )
        assert file_


def test_delete_file():
    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    files = s.file.get_files(business_id=business_id, app_id=app_id)
    for file in files:
        s.file.delete_file(
            business_id=business_id,
            app_id=app_id,
            file_id=file['id'],
        )
    files = s.file.get_files(business_id=business_id, app_id=app_id)
    assert not files


def test_encode_file_name():
    s.file._encode_file_name()


def test_decode_file_name():
    s.file._decode_file_name()


def test_get_files_by_string_matching():
    s.file._get_files_by_string_matching()


def test_get_files_by_name_prefix():
    s.file._get_files_by_name_prefix()


def test_delete_file_by_name():
    s.file._delete_file_by_name()


def test_replace_file_name():
    s.file._replace_file_name()


def test_get_file_by_name():
    file = s.file.get_file_by_name(
        business_id=business_id,
        app_name='test',
        file_name='test_file_metadata_api',
        get_file_object=False,
    )
    assert file

    file = s.file.get_file_by_name(
        business_id=business_id,
        app_name='test',
        file_name='test_file_metadata_api',
        get_file_object=True,
    )
    assert file


def test_get_file_by_creation_date():
    s.file.get_file_by_creation_date()


def test_get_files_by_name_prefix():
    s.file.get_files_by_name_prefix()


def test_get_files_by_string_matching():
    files: List[Dict] = s.file._get_files_by_string_matching(
        business_id=business_id, string_match='test',
    )
    assert files

    files: List[Dict] = s.file._get_files_by_string_matching(
        business_id=business_id, string_match='test', app_name='test',
    )
    assert files

    files: List[Dict] = s.file._get_files_by_string_matching(
        business_id=business_id, string_match='faile', app_name='test',
    )
    assert not files

    files: List[Dict] = s.file._get_files_by_string_matching(
        business_id=business_id, string_match='test', app_name='fail'
    )
    assert not files


def test_post_dataframe():
    s.file.post_dataframe()


def test_get_dataframe():
    s.file.get_dataframe()


test_get_file_by_name()
test_get_files_by_string_matching()
test_create_file()
test_get_file()
test_get_files()
test_delete_file()
