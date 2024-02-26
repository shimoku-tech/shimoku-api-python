from shimoku import Client


def stacked_bar_chart(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "stacked-bar-chart")

    shimoku_client.plt.stacked_bar(
        data="stacked data",
        x="Segment",
        x_axis_name="Distribution and weight of the Drivers",
        order=0,
        show_values=["Price"],
    )
