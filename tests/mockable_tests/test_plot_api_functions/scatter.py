import pandas as pd
from os import path
from shimoku import Client

data_path = path.join(path.dirname(path.abspath(__file__)), "data")


def scatter(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "scatter-test")

    shimoku_client.plt.scatter(
        data="main data",
        point_fields=[("x", "y")],
        order=0,
        cols_size=6,
        variant="clean",
    )
    scatter_data = pd.read_csv(path.join(data_path, "scatter_test.csv"))[
        [
            "AgeGroup1",
            "AgeGroup2",
            "AgeGroup3",
            "AllGroupAge",
            "WeightGroup1",
            "WeightGroup2",
            "WeightGroup3",
            "AllGroupWeight",
        ]
    ]
    shimoku_client.plt.scatter(
        data=scatter_data,
        point_fields=[
            ("AgeGroup1", "WeightGroup1"),
            ("AgeGroup2", "WeightGroup2"),
            ("AgeGroup3", "WeightGroup3"),
            ("AllGroupAge", "AllGroupWeight"),
        ],
        title="Age Weight correlation study",
        x_axis_name="Age",
        y_axis_name="Weight",
        order=1,
        rows_size=4,
        cols_size=6,
    )
