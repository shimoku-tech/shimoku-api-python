from shimoku import Client
from .data.free_echarts import free_echarts_data, free_echarts_options


def free_echarts(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts")

    shimoku_client.plt.free_echarts(
        data=free_echarts_data,
        options=free_echarts_options,
        fields=["product", "2015", "2016", "2017"],
        order=0,
        rows_size=2,
        cols_size=12,
    )
