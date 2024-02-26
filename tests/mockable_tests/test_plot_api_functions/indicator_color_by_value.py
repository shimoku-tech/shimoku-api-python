from shimoku import Client
from .data.indicator_color_by_value import indicator_color_by_value_data


def indicator_color_by_value(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "indicators-by-value")
    shimoku_client.plt.indicator(
        data=indicator_color_by_value_data,
        cols_size=12,
        rows_size=1,
        order=4,
        color_by_value=True,
    )
