from shimoku import Client
from .data.stacked_area import stacked_area_data


def stacked_area_chart(shimoku_client: Client):
    print("test_area_chart")
    shimoku_client.set_menu_path("test-free-echarts", "stacked-area-chart")

    shimoku_client.plt.stacked_area(
        data=stacked_area_data,
        x="Weekday",
        x_axis_name="Visits per weekday",
        order=0,
    )
