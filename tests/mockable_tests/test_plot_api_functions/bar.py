from shimoku import Client
from .data.default import data


def bar(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "bar-test")
    shimoku_client.plt.bar(
        data=data,
        x="date",
        y=["x", "y"],
        x_axis_name="Date",
        y_axis_name="Revenue",
        order=0,
        rows_size=2,
        cols_size=12,
    )
    shimoku_client.plt.bar(data="main data", x="date", order=1)
