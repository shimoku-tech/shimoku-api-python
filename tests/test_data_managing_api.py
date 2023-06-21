""""""
import json
import time
from os import getenv
from typing import Dict, List

import pandas as pd

import shimoku_api_python as shimoku


access_token: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
verbosity: str = getenv('VERBOSITY')


s = shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
    verbosity=verbosity
)
s.set_workspace(uuid=business_id)
s.set_menu_path('data_set_test')
s.plt.clear_menu_path()

# Fixtures
data: Dict = {
    'a': [x for x in range(10)],
    'b': [x ** 2 for x in range(10)],
}
data_oriented: List = pd.DataFrame(data).to_dict(orient='records')
df = pd.DataFrame(data)
data_json: str = json.dumps(data_oriented)


def test_data_sets():
    global data_oriented
    s.data.append_to_data_set(name='test-data-set', data=data_oriented)
    time.sleep(5)
    data_ = s.data.get_data_from_data_set(name='test-data-set')
    data_ = sorted(data_, key=lambda x: x['intField1'])
    data_oriented = sorted(data_oriented, key=lambda x: x['a'])
    for i in range(len(data_oriented)):
        assert data_[i]['intField1'] == data_oriented[i]['a']
        assert data_[i]['intField2'] == data_oriented[i]['b']

    s.data.append_to_data_set(name='test-data-set', data=data_oriented)
    time.sleep(5)
    data_ = s.data.get_data_from_data_set(name='test-data-set')
    data_ = sorted(data_, key=lambda x: x['intField1'])
    for i in range(len(data_oriented)):
        assert data_[i*2]['intField1'] == data_oriented[i]['a']
        assert data_[i*2]['intField2'] == data_oriented[i]['b']

    s.data.replace_data_from_data_set(name='test-data-set', data=data_oriented)
    time.sleep(5)
    data_ = s.data.get_data_from_data_set(name='test-data-set')
    data_ = sorted(data_, key=lambda x: x['intField1'])
    for i in range(len(data_oriented)):
        assert data_[i]['intField1'] == data_oriented[i]['a']
        assert data_[i]['intField2'] == data_oriented[i]['b']

    s.data.delete_data_set(name='test-data-set')
    assert not s.data.get_data_from_data_set(name='test-data-set')


test_data_sets()
