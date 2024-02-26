from shimoku import Client


def marked_line_chart(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "Marked Line Chart")
    shimoku_client.plt.marked_line(
        data="table",
        x="date",
        marks=[("first segment", 0, 1), ("second segment", 2, 3)],
        order=0,
        rows_size=2,
        cols_size=12,
        y=["x", "y"],
    )
