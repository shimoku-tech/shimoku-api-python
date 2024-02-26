import pandas as pd
from os import path
from shimoku import Client
from .data.default import data
from .data.pie import pie_data

data_path = path.join(path.dirname(path.abspath(__file__)), "data")


def doughnut(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "doughnut")

    shimoku_client.plt.doughnut(data=data, names="date", values="x", order=0)
    shimoku_client.plt.doughnut(data=pie_data, names="name", values="value", order=1)

    df = pd.read_csv(path.join(data_path, "test_stack_distribution.csv"))

    value_columns = [col for col in df.columns if col != "Segment"]
    df = df[["Segment"] + value_columns]

    aux_doughnut_data = pd.DataFrame(columns=["name", "value"])
    df_transposed = df.transpose().reset_index().drop(0)
    value_columns = [col for col in df_transposed.columns if col != "index"]
    aux_doughnut_data["value"] = df_transposed[value_columns].apply(
        lambda row: sum(row), axis=1
    )
    aux_doughnut_data["name"] = df_transposed["index"]
    shimoku_client.plt.doughnut(
        data=aux_doughnut_data,
        values="value",
        names="name",
        order=2,
        rows_size=3,
        cols_size=6,
    )
