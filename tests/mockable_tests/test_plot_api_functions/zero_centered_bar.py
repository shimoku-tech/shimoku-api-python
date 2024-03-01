from shimoku import Client


def zero_centered_bar_chart(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "zero-centered-bar-test")

    shimoku_client.plt.zero_centered_bar(
        data="zero centered data",
        x="Name",
        y="y",
        order=0,
    )

    shimoku_client.plt.zero_centered_bar(
        data="zero centered data",
        x="Name",
        y=["y", "z", "a"],
        x_axis_name="Axis x",
        y_axis_name="Axis y",
        title="Title",
        order=1,
        rows_size=3,
        cols_size=10,
        padding="0,0,0,1",
    )
