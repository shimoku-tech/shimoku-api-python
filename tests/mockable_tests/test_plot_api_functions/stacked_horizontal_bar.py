from shimoku import Client


def stacked_horizontal_bar_chart(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "horizontal-stacked-bar-chart")

    shimoku_client.plt.stacked_horizontal_bar(
        data="stacked data",
        x="Segment",
        order=0,
        x_axis_name="Distribution and weight of the Drivers",
    )
