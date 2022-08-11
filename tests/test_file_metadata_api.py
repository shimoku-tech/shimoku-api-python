""""""
from os import getenv
from typing import Dict, List
import unittest

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
    s.file._get_file_by_name()


def test_get_file_by_date():
    s.file.get_file_by_date()


def test_get_files_by_name_prefix():
    s.file.get_files_by_name_prefix()


def test_get_files_by_string_matching():
    s.file.get_files_by_string_matching()


def test_post_dataframe():
    s.file.post_dataframe()


def test_get_dataframe():
    s.file.get_dataframe()


def test_get_file():
    s.file._get_file()


def test_create_file():
    s.file._create_file()


def test_delete_file():
    s.file._delete_file()

