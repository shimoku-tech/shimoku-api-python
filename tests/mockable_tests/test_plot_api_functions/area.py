from shimoku import Client


def area(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "area-test")
    shimoku_client.plt.area(data="main data", x="date", order=0, variant="clean")
    shimoku_client.plt.area(
        data="main data", x="date", order=1, rows_size=2, cols_size=12
    )
