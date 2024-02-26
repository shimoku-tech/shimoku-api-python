from shimoku import Client
from .data.table_with_labels import table_with_labels_data
import numpy as np


def table_with_labels(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "table-test-with-labels")
    shimoku_client.plt.table(
        data=table_with_labels_data,
        order=0,
        rows_size=10,
        page_size=100,
        initial_sort_column="date",
        categorical_columns=["filtA", "filtB"],
        label_columns={
            ("x", "outlined"): {
                3: [0, 255, 0],
                4: "#42F548",
                5: "#666666",
                6: "#4287f5",
                7: [255, 0, 0],
            },
            ("y", "outlined"): {
                (0, 25): "red",
                (25, 50): "orange",
                (50, 75): "yellow",
                (75, np.inf): "green",
            },
            "z": {
                (0, 25): [100, 100, 100],
                (25, 50): "yellow",
                (50, 75): "orange",
                (75, np.inf): "red",
            },
            "a": {
                (0, 25): [100, 100, 100],
                (25, 50): "yellow",
                (50, 75): "orange",
                (75, np.inf): "red",
            },
            "filtA": "#666666",
            ("filtB", "outlined"): [125, 54, 200],
            "name": "warning",
            "name2": {
                "Ana": "active",
                "Laura": "error",
                "Audrey": "warning",
                "Jose": "caution",
                "Jorge": "main",
            },
            ("name3", "outlined"): "neutral",
        },
    )
