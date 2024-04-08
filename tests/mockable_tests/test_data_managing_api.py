""""""
import json
import time

from os import getenv
from typing import Dict
from unittest import TestCase

import pandas as pd

from shimoku.exceptions import DataError
from shimoku import Client

from utils import initiate_shimoku

TEST_DATA_SET_NAME = "test-data-set"


class TestDataSets(TestCase):

    def sleep_cloud(self):
        if not self.shimoku_client.playground:
            time.sleep(5)

    def setUp(self):
        data: Dict = {
            "a": [x for x in range(10)],
            "b": [x ** 2 for x in range(10)],
        }
        self.data_oriented = sorted(
            pd.DataFrame(data).to_dict(orient="records"), key=lambda x: x["a"]
        )
        self.datajson: str = json.dumps(self.data_oriented)
        self.bad_dfs = [
            [{"a": 1, "b": 2}, {"a": 1, "b": 2, "c": 3}],
            [{"a": 1, "b": 2}, {"a": 1, "b": "c"}],
            [{"a": 1, "b": 2}, {"a": None, "b": 2}],
        ]
        self.shimoku_client: Client = initiate_shimoku()
        self.shimoku_client.set_workspace(getenv("BUSINESS_ID"))
        self.shimoku_client.set_menu_path(TEST_DATA_SET_NAME)
        self.shimoku_client.plt.clear_menu_path()
        
    def test_data_sets_CRUD(self):
        self.shimoku_client.data.append_to_data_set(name=TEST_DATA_SET_NAME, data=self.data_oriented)
        self.sleep_cloud()
        data = self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)
        data = sorted(data, key=lambda x: x["orderField1"])
        for i in range(len(self.data_oriented)):
            assert data[i]["intField1"] == self.data_oriented[i]["a"]
            assert data[i]["intField2"] == self.data_oriented[i]["b"]
            assert data[i]["orderField1"] == i

        self.shimoku_client.data.append_to_data_set(name=TEST_DATA_SET_NAME, data=self.data_oriented)
        self.sleep_cloud()
        data = self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)
        data = sorted(data, key=lambda x: x["orderField1"])
        for i in range(len(self.data_oriented)):
            assert data[i * 2]["intField1"] == self.data_oriented[i]["a"]
            assert data[i * 2]["intField2"] == self.data_oriented[i]["b"]
            assert data[i * 2]["orderField1"] == i

        self.shimoku_client.data.replace_data_from_data_set(name=TEST_DATA_SET_NAME, data=self.data_oriented)
        self.sleep_cloud()
        data = self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)
        data = sorted(data, key=lambda x: x["orderField1"])
        assert len(data) == len(self.data_oriented)
        for i in range(len(self.data_oriented)):
            assert data[i]["intField1"] == self.data_oriented[i]["a"]
            assert data[i]["intField2"] == self.data_oriented[i]["b"]
            assert data[i]["orderField1"] == i

        self.shimoku_client.data.delete_data_set(name=TEST_DATA_SET_NAME)
        assert not self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)

    def test_delete_data_points(self):
        self.shimoku_client.data.append_to_data_set(name=TEST_DATA_SET_NAME, data=self.data_oriented)
        self.sleep_cloud()
        data = self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)
        data = sorted(data, key=lambda x: x["orderField1"])
        for i in range(len(self.data_oriented)):
            assert data[i]["intField1"] == self.data_oriented[i]["a"]
            assert data[i]["intField2"] == self.data_oriented[i]["b"]
            assert data[i]["orderField1"] == i

        self.shimoku_client.data.delete_data_from_data_set(name=TEST_DATA_SET_NAME)
        self.sleep_cloud()
        data = self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)
        assert not data

        self.shimoku_client.data.delete_data_set(name=TEST_DATA_SET_NAME)
        assert not self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)

    def test_linear_update(self):
        self.shimoku_client.data.append_to_data_set(name=TEST_DATA_SET_NAME, data=self.data_oriented[:5])
        self.sleep_cloud()

        data = self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)
        data = sorted(data, key=lambda x: x["orderField1"])

        for i in range(5):
            assert data[i]["intField1"] == self.data_oriented[i]["a"]
            assert data[i]["intField2"] == self.data_oriented[i]["b"]
            assert data[i]["orderField1"] == i

        modified_oriented_data = [{"a": dp["a"] + 10, "b": dp["b"] + 10} for dp in self.data_oriented]
        self.shimoku_client.data.linear_update_data_from_data_set(name=TEST_DATA_SET_NAME, data=modified_oriented_data)
        self.sleep_cloud()
        data = self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)
        data = sorted(data, key=lambda x: x["orderField1"])

        for i in range(10):
            assert data[i]["intField1"] == modified_oriented_data[i]["a"]
            assert data[i]["intField2"] == modified_oriented_data[i]["b"]
            assert data[i]["orderField1"] == i

        modified_oriented_data = [{"a": 0, "b": 0}]
        self.shimoku_client.data.linear_update_data_from_data_set(name=TEST_DATA_SET_NAME, data=modified_oriented_data)
        self.sleep_cloud()

        data = self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)
        assert len(data) == 1
        assert data[0]["intField1"] == 0
        assert data[0]["intField2"] == 0
        assert data[0]["orderField1"] == 0

        self.shimoku_client.data.delete_data_set(name=TEST_DATA_SET_NAME)
        assert not self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME)
         
    def test_bad_dfs(self):
        for i, bad_df in enumerate(self.bad_dfs):
            with self.assertRaises(DataError):
                self.shimoku_client.data.append_to_data_set(name=f"test-data-set_{i}", data=bad_df)

    def test_bad_append_to_existing_df(self):
        self.shimoku_client.data.replace_data_from_data_set(name=TEST_DATA_SET_NAME, data=self.data_oriented)
        self.sleep_cloud()
        print(self.shimoku_client.data.get_data_from_data_set(name=TEST_DATA_SET_NAME))
        for i, bad_df in enumerate(self.bad_dfs):
            bad_df_aux = [bad_df[1]]
            with self.assertRaises(DataError):
                self.shimoku_client.data.append_to_data_set(name=TEST_DATA_SET_NAME, data=bad_df_aux)
