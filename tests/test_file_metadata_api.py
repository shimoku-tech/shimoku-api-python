""""""
from os import getenv
import unittest

import pandas as pd

from shimoku_api_python.exceptions import CacheError
import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')
verbosity: str = getenv('VERBOSITY')

s = shimoku.Client(
    access_token=api_key,
    universe_id=universe_id,
    environment=environment,
    verbosity=verbosity,
    async_execution=True
)
s.set_workspace(uuid=business_id)
s.set_menu_path('File test')
s.menu_paths.delete_all_menu_path_files(name='File test', with_shimoku_generated=True)


def test_general_files():
    data = {
        'a': [1, 2, 3],
        'b': [1, 4, 9],
    }
    df = pd.DataFrame(data)
    file_object = df.to_csv(index=False)
    filename = 'helloworld.csv'
    s.io.post_object(file_name=filename, obj=file_object)

    files = s.menu_paths.get_menu_path_files(name='File test')
    assert 'helloworld.csv' in [file['name'] for file in files]

    class MyTestCase(unittest.TestCase):
        def test_cant_create_duplicate_files(self):
            with self.assertRaises(CacheError):
                s.io.post_object(file_name=filename, obj=file_object, overwrite=False)
                s.run()

    t = MyTestCase()
    t.test_cant_create_duplicate_files()

    s.io.delete_file(file_name=filename)
    files = s.menu_paths.get_menu_path_files(name='File test')
    assert 'helloworld.csv' not in [file['name'] for file in files]


def test_tags_and_metadata():
    previous_len_files = len(s.menu_paths.get_menu_path_files(name='File test'))
    s.io.post_object(
        file_name='Shimoku generated file', obj=b'',
        tags=['shimoku_generated', 'IO'], metadata={'business_id': business_id}
    )
    len_files = len(s.menu_paths.get_menu_path_files(name='File test'))
    assert len_files == previous_len_files
    len_files = len(s.menu_paths.get_menu_path_files(name='File test', with_shimoku_generated=True))
    assert len_files == previous_len_files + 1
    file = s.io.get_object(file_name='Shimoku generated file')
    assert file == b''
    file_metadata = s.io.get_file_metadata(file_name='Shimoku generated file')
    assert file_metadata['metadata']['business_id'] == business_id
    assert file_metadata['tags'] == ['shimoku_generated', 'IO']
    s.io.delete_file(file_name='Shimoku generated file', with_shimoku_generated=True)
    len_files = len(s.menu_paths.get_menu_path_files(name='File test', with_shimoku_generated=True))
    assert len_files == previous_len_files


def test_get_object():
    file_name = 'helloworld'
    object_data = b''
    s.io.post_object(file_name=file_name, obj=object_data)
    file = s.io.get_object(file_name=file_name)
    assert file == object_data


def test_post_dataframe():
    file_name: str = 'df-test'
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [1, 4, 9]})
    s.io.post_dataframe(file_name, df=df)
    file = s.io.get_dataframe(file_name=file_name)
    assert file.to_dict() == df.to_dict()


def test_post_get_model():
    from sklearn import svm
    from sklearn import datasets

    clf = svm.SVC()
    X, y = datasets.load_iris(return_X_y=True)
    clf.fit(X, y)

    s.io.post_ai_model(model_name='model-test', model=clf)
    clf2 = s.io.get_ai_model(model_name='model-test')

    assert type(clf2) == type(clf)


def test_big_data():
    filename = '../data/bulidata.csv'
    df = pd.read_csv(filename)
    df.reset_index(inplace=True)

    s.io.post_batched_dataframe(file_name='test-big-df', df=df)

    dataset: pd.DataFrame = s.io.get_batched_dataframe(file_name='test-big-df')
    assert len(dataset) == len(df)

    s.io.post_object(file_name='test-big-df.csv', obj=df.to_csv(index=False))


def test_more_than_100_files():
    menu_path_mt100 = 'more than 100 files test'
    s.set_menu_path(menu_path_mt100)
    s.menu_paths.delete_all_menu_path_files(name=menu_path_mt100)
    for i in range(201):
        s.io.post_object(file_name=f'file_{i}.txt', obj=f'Content of file {i}')
    s.pop_out_of_menu_path()
    s.run()
    s.disable_caching()
    assert len(s.menu_paths.get_menu_path_files(name=menu_path_mt100)) == 201
    s.menu_paths.delete_all_menu_path_files(name=menu_path_mt100)
    assert len(s.menu_paths.get_menu_path_files(name=menu_path_mt100)) == 0
    s.menu_paths.delete_menu_path(name=menu_path_mt100)


test_general_files()
test_get_object()
test_post_dataframe()
test_tags_and_metadata()
test_post_get_model()
test_big_data()
test_more_than_100_files()

s.run()
