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
    business_id=business_id
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

    file = s.io._create_file(
        business_id=business_id, app_id=app_id,
        file_metadata=file_metadata, file_object=file_object,
    )
    assert file


def test_get_files():
    test_create_file()

    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    files = s.io.get_files(business_id=business_id, app_id=app_id)
    assert files

    test_delete_file()


def test_get_file():
    test_create_file()

    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    files = s.io.get_files(business_id=business_id, app_id=app_id)
    for file in files:
        file_ = s.io._get_file(
            business_id=business_id,
            app_id=app_id,
            file_id=file['id'],
        )
        try:
            assert file_
            break
        except AssertionError:
            continue
    else:
        raise Exception('No files found')

    test_delete_file()


def test_delete_file():
    apps = s.business.get_business_apps(business_id)
    app_id = [app for app in apps if app['name'] == 'test'][0]['id']

    files = s.io.get_files(business_id=business_id, app_id=app_id)
    for file in files:
        s.io._delete_file(
            business_id=business_id,
            app_id=app_id,
            file_id=file['id'],
        )

    files = s.io.get_files(business_id=business_id, app_id=app_id)
    assert not files


def test_encode_file_name():
    file_name = 'helloworld'
    today = dt.date.today()
    new_file_name = s.io._encode_file_name(file_name=file_name, date=today)
    assert new_file_name == f'helloworld_date:{dt.date.today().isoformat()}'


def test_decode_file_name():
    file_name = f'helloworld_date:{dt.date.today().isoformat()}'
    new_file_name = s.io._decode_file_name(file_name)
    assert new_file_name == 'helloworld'


def test_get_file_date():
    today = dt.date.today()
    file_name = f'helloworld_date:{today.isoformat()}'
    date = s.io._get_file_date(file_name)
    assert date == today


def test_get_all_files_by_app_name():
    test_create_file()
    files: List[Dict] = s.io.get_all_files_by_app_name(app_name='test')
    assert files
    test_delete_file()


def test_get_files_by_string_matching():
    test_create_file()

    files: List[Dict] = s.io._get_files_by_string_matching(string_match='hello')
    assert files

    files: List[Dict] = s.io._get_files_by_string_matching(
        string_match='hello', app_name='test',
    )
    assert files

    files: List[Dict] = s.io._get_files_by_string_matching(
        string_match='fail', app_name='test',
    )
    assert not files

    files: List[Dict] = s.io._get_files_by_string_matching(
        string_match='hello', app_name='fail'
    )
    assert not files

    test_delete_file()


def test_get_file_by_name():
    test_create_file()

    file = s.io.get_file_by_name(
        app_name='test',
        file_name='helloworld',
        get_file_object=False,
    )
    assert file

    file = s.io.get_file_by_name(
        app_name='test',
        file_name='helloworld',
        get_file_object=True,
    )
    assert file

    test_delete_file()


def test_get_all_files_by_date():
    test_post_object()

    today = dt.date.today().isoformat()
    files: List[Dict] = s.io.get_files_by_date(
        date=today,
        app_name='test',
    )
    assert files

    tomorrow = today + dt.timedelta(1)
    files: List[Dict] = s.io.get_file_by_creation_date(
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
    s.io.post_object(
        app_name=app_name,
        file_name=file_name,
        object_data=object_data
    )

    today = dt.date.today()
    files: List[Dict] = s.io.get_all_files_by_date(
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
    s.io.post_object(
        app_name=app_name,
        file_name=file_name,
        object_data=object_data
    )

    file: Dict = s.io.get_file_by_date(
        date=today,
        file_name='helloworld',
        app_name='test',
    )

    assert file

    file_object: bytes = s.io.get_file_by_date(
        date=today,
        file_name='helloworld',
        app_name='test',
        get_file_object=True,
    )
    assert len(file_object) == 1
    assert file_object[0] == object_data

    tomorrow = today + dt.timedelta(1)
    file: Dict = s.io.get_file_by_date(
        date=tomorrow,
        app_name='test',
        file_name='helloworld',
    )
    assert not file


def test_get_files_with_max_date():
    file_name = 'helloworld'
    app_name = 'test'
    object_data = b''
    s.io.post_object(
        app_name=app_name,
        file_name=file_name,
        object_data=object_data
    )

    files = s.io.get_files_with_max_date(
        app_name='test',
        file_name='helloworld',
    )
    assert len(files) == 1
    assert files[0]['name'] == f'helloworld_date:{dt.date.today().isoformat()}'

    files_object = s.io.get_files_with_max_date(
        app_name='test',
        file_name='helloworld',
        get_file_object=True,
    )
    assert len(files_object) == 1
    assert files_object[0] == object_data

    test_delete_file()


def test_get_files_by_name_prefix():
    test_create_file()

    files: List[Dict] = s.io.get_files_by_name_prefix(
        name_prefix='hello', app_name='test',
    )
    assert files

    test_delete_file()


def test_delete_files_by_name_prefix():
    class MyTestCase(unittest.TestCase):
        def test_fake_business(self):
            with self.assertRaises(ValueError):
                s.io.get_file_by_name(
                    file_name='helloworld',
                    app_name='test'
                )

    test_create_file()

    s.io.delete_files_by_name_prefix(
        name_prefix='helloworld',
        app_name='test',
    )

    t = MyTestCase()
    t.test_fake_business()


def test_replace_file_name():
    s.io._replace_file_name()


def test_post_object():
    file_name = 'helloworld'
    app_name = 'test'
    object_data = b''

    file = s.io.post_object(
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

    s.io.post_object(
        app_name=app_name,
        file_name=file_name,
        object_data=object_data
    )

    files = s.io.get_object(
        app_name=app_name,
        file_name=file_name,
    )
    assert len(files) == 1
    assert files[0] == object_data

    test_delete_file()


def test_post_dataframe():
    d = {'a': [1, 2, 3], 'b': [1, 4, 9]}
    df = pd.DataFrame(d)
    file: Dict = s.io.post_dataframe(
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
    file: Dict = s.io.post_dataframe(
        app_name='test',
        file_name=file_name,
        df=df_,
    )
    assert file

    df: pd.DataFrame = s.io.get_dataframe(
        app_name='test',
        file_name=file_name,
    )
    assert df.to_dict() == df_.to_dict()

    test_delete_file()


def test_post_get_model():
    import pickle

    from sklearn import svm
    from sklearn import datasets

    clf = svm.SVC()
    X, y = datasets.load_iris(return_X_y=True)
    clf.fit(X, y)

    m: bytes = pickle.dumps(clf)

    s.io.post_object(
        app_name='test',
        file_name='model-test',
        object_data=m
    )

    m2 = s.io.get_object(
        app_name='test',
        file_name='model-test',
    )
    assert len(m2) == 1
    assert m2[0] == m

    s.io.post_ai_model(
        app_name='test',
        model_name='model-object-test',
        model=clf,
    )

    clf2 = s.io.get_ai_model(
        app_name='test',
        model_name='model-object-test',
    )

    assert type(clf2) == type(clf)


def test_big_data():
    filename = '../data/classification_dataset_short.csv'
    df = pd.read_csv(filename)
    df.reset_index(inplace=True)

    s.io.post_dataframe(
        app_name='test',
        file_name='test-big-df',
        df=df
    )

    dataset: pd.DataFrame = s.io.get_dataframe(
        app_name='test',
        file_name='test-big-df'
    )
    assert len(dataset) == len(df)


test_create_file()
test_get_file()
test_get_files()
test_delete_file()

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
test_get_files_with_max_date()
test_get_file_by_date()

test_post_dataframe()
test_post_get_dataframe()
test_post_get_model()

test_big_data()

# TODO pending
# test_replace_file_name()

# TODO pending to have a createdAt
# test_get_all_files_by_creation_date()
# test_get_file_by_creation_date()
# test_get_last_created_target_file()
