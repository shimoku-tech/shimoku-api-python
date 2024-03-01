from shimoku import Client


def funnel(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "funnel-test")

    shimoku_client.plt.funnel(
        data="funnel data",
        order=0,
        title="Funnel Chart",
        names="name",
        values="value",
    )

    shimoku_client.plt.funnel(
        data="funnel data",
        names="name",
        values="value",
        order=1,
        rows_size=2,
        cols_size=12,
    )
