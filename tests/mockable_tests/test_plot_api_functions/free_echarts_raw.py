from shimoku import Client
from .data.free_echarts_raw import free_echarts_raw_options


def free_echarts_raw(shimoku_client: Client):
    # https://echarts.apache.org/examples/en/editor.html?c=area-time-axis
    shimoku_client.set_menu_path("test-free-echarts", "raw")

    shimoku_client.plt.free_echarts(
        raw_options=free_echarts_raw_options,
        order=0,
    )
