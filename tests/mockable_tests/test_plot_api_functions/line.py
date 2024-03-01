from shimoku import Client


def line(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "line-test")
    shimoku_client.plt.line(data="main data", x="date", order=0, variant="minimal")
    shimoku_client.plt.line(
        data="main data", x="date", order=1, rows_size=2, cols_size=12
    )
