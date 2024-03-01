from shimoku import Client
from .data.indicator import indicator_data_variant_1, indicator_data_variant_2


def indicator(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "indicators")

    order = shimoku_client.plt.indicator(data=indicator_data_variant_1, order=0)
    order = shimoku_client.plt.indicator(
        data=indicator_data_variant_1 + indicator_data_variant_1[2:], order=order
    )

    shimoku_client.plt.indicator(
        data=indicator_data_variant_2, order=order, rows_size=1, cols_size=12
    )

    shimoku_client.set_menu_path("test", "indicators-vertical")
    order = shimoku_client.plt.indicator(
        data=indicator_data_variant_2 + indicator_data_variant_2,
        order=0,
        rows_size=1,
        cols_size=6,
        vertical="Title of the indicators",
    )
    order = shimoku_client.plt.indicator(
        data=indicator_data_variant_2,
        order=order,
        rows_size=2,
        cols_size=4,
        vertical=True,
    )
    order = shimoku_client.plt.indicator(
        data=indicator_data_variant_2[0],
        order=order,
        rows_size=8,
        cols_size=2,
        vertical="Title of the indicator",
    )
    shimoku_client.plt.indicator(
        data=indicator_data_variant_2[0],
        order=order,
        rows_size=8,
        cols_size=12,
        vertical=True,
    )
