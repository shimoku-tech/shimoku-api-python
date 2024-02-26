from shimoku import Client
from .data.suburst import sunburst_data


def sunburst(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "sunburst")
    # Using the data set from the tree test
    shimoku_client.plt.sunburst(data="tree_data", order=0)
    shimoku_client.plt.sunburst(data=sunburst_data, order=1)
