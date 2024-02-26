from shimoku import Client
from .data.sankey import sankey_data


def sankey(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "sankey-test")

    shimoku_client.plt.sankey(
        data=sankey_data, sources="source", targets="target", values="value", order=0
    )
