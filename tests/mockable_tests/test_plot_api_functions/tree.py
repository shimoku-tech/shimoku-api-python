from shimoku import Client
from .data.suburst import sunburst_data


def tree(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "tree-test")

    shimoku_client.plt.tree(data=sunburst_data, order=0)
    shimoku_client.plt.tree(
        data="tree_data", order=1, rows_size=4, cols_size=12, title="Tree", radial=True
    )
    shimoku_client.plt.tree(
        data="tree_data",
        order=2,
        rows_size=2,
        cols_size=12,
        title="Tree",
        vertical=True,
    )
    shimoku_client.plt.tree(
        data="tree_data",
        order=3,
        rows_size=4,
        cols_size=12,
        title="Tree",
        radial=True,
        vertical=True,
    )
