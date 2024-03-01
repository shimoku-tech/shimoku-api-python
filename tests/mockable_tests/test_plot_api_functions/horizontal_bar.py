from shimoku import Client
from .data.horizontal_bar import horizontal_bar_data


def horizontal_bar_chart(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "horizontal-bar-test")

    shimoku_client.plt.horizontal_bar(data=horizontal_bar_data, x="name", order=0)

    shimoku_client.plt.horizontal_bar(
        data=horizontal_bar_data,
        x="name",
        x_axis_name="Axis x",
        y_axis_name="Axis y",
        title="Title",
        order=1,
        rows_size=3,
        cols_size=10,
        padding="0,0,0,1",
    )
