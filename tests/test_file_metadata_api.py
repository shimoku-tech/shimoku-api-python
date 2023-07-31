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
# s.menu_paths.delete_all_menu_path_files(name='File test')


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


def test_get_object():
    file_name = 'helloworld'
    object_data = b''
    s.io.post_object(file_name, object_data)
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


test_general_files()
test_get_object()
test_post_dataframe()
test_post_get_model()
test_big_data()
