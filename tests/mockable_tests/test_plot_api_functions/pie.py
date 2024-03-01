from shimoku import Client
from .data.pie import pie_data


def pie(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "pie-test")

    shimoku_client.plt.pie(data="main data", names="date", values="x", order=0)
    shimoku_client.plt.pie(
        data=pie_data, names="name", values="value", order=1, rows_size=2, cols_size=12
    )
