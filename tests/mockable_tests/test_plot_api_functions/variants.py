from shimoku import Client


def variants(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "Variants")

    shimoku_client.plt.stacked_bar(
        data="stacked data",
        order=0,
        cols_size=6,
        x="Segment",
        variant="clean shadow",
        show_values="all",
    )
    shimoku_client.plt.stacked_horizontal_bar(
        data="stacked data",
        order=1,
        cols_size=6,
        x="Segment",
        variant="minimal shadow",
        show_values="all",
    )
    shimoku_client.plt.bar(
        data="table",
        order=2,
        cols_size=6,
        x="date",
        variant="shadow",
        show_values=["x"],
    )
    shimoku_client.plt.horizontal_bar(
        data="horizontal bar",
        x="name",
        order=3,
        cols_size=6,
        show_values=["value"],
        variant="clean shadow",
    )
    shimoku_client.plt.bar(
        data="table",
        order=4,
        cols_size=6,
        x="date",
        variant="clean thin",
        show_values=["x"],
    )
    shimoku_client.plt.horizontal_bar(
        data="horizontal bar",
        x="name",
        order=5,
        cols_size=6,
        show_values=["value"],
        variant="clean thin",
    )
    shimoku_client.plt.stacked_bar(
        data="stacked data",
        order=6,
        cols_size=6,
        x="Segment",
        variant="thin",
        show_values="all",
    )
    shimoku_client.plt.stacked_horizontal_bar(
        data="stacked data",
        order=7,
        cols_size=6,
        x="Segment",
        variant="clean thin",
        show_values="all",
    )
    shimoku_client.plt.area(
        data="table",
        order=8,
        cols_size=3,
        rows_size=2,
        x="date",
        y="x",
        variant="minimal",
    )
    shimoku_client.plt.line(
        data="table",
        order=9,
        cols_size=3,
        rows_size=2,
        x="date",
        y="x",
        variant="minimal",
    )
