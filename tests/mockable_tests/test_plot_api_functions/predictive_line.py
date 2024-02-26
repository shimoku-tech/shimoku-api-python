from shimoku import Client


def predictive_line(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "predictive-line-test")
    shimoku_client.plt.predictive_line(
        data="main data",
        x="date",
        min_value_mark=3,
        max_value_mark=4,
        order=1,
        rows_size=2,
        cols_size=12,
    )
