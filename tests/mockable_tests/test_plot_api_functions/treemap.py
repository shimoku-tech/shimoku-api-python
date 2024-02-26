from shimoku import Client
from .data.suburst import sunburst_data
from .data.tree import tree_data


def treemap(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "treemap-test")
    # Using the data set from the tree test
    shimoku_client.plt.treemap(data=tree_data, order=0)
    shimoku_client.plt.treemap(data=sunburst_data, order=1)
