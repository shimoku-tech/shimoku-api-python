import pandas as pd
from os import path
from shimoku import Client
from .data.pie import pie_data

data_path = path.join(path.dirname(path.abspath(__file__)), "data")


def rose(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "rose")
    shimoku_client.plt.rose(data="main data", names="date", values="x", order=0)
    shimoku_client.plt.rose(data=pie_data, names="name", values="value", order=1)

    df = pd.read_csv(path.join(data_path, "test_stack_distribution.csv"))

    value_columns = [col for col in df.columns if col != "Segment"]
    df = df[["Segment"] + value_columns]

    rose_data = pd.DataFrame(columns=["name", "value"])
    df_transposed = df.transpose().reset_index().drop(0)
    value_columns = [col for col in df_transposed.columns if col != "index"]
    rose_data["value"] = df_transposed[value_columns].apply(
        lambda row: sum(row), axis=1
    )
    rose_data["name"] = df_transposed["index"]
    shimoku_client.plt.rose(
        data=rose_data, values="value", names="name", order=2, rows_size=3, cols_size=6
    )
