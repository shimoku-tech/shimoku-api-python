from shimoku import Client
from .data.bentobox_indicator import bentobox_indicator_data


def bentobox(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "bentobox-test")

    shimoku_client.plt.set_bentobox(cols_size=8, rows_size=3)

    shimoku_client.plt.indicator(
        data=bentobox_indicator_data, order=0, rows_size=10, cols_size=12
    )
    shimoku_client.plt.indicator(
        data=bentobox_indicator_data, order=1, rows_size=10, cols_size=12
    )
    shimoku_client.plt.bar(
        data="main data", x="date", y=["x", "y"], order=2, rows_size=26, cols_size=24
    )

    shimoku_client.plt.pop_out_of_bentobox()
