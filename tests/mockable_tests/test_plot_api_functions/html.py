from shimoku import Client
from .data.html import html_data


def html(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "html-test")

    shimoku_client.plt.html(html=html_data, order=0)
    shimoku_client.plt.html(html=html_data, order=1, rows_size=2, cols_size=12)
