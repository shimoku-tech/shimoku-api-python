from shimoku import Client


def heatmap(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "heatmap")

    shimoku_client.plt.heatmap(
        data="heatmap data",
        x="xAxis",
        y="yAxis",
        values="value",
        order=0,
        calculate_color_range=True,
        variant="minimal",
    )

    shimoku_client.plt.heatmap(
        data="heatmap data",
        x="xAxis",
        y="yAxis",
        values="value",
        order=1,
        continuous=True,
        title="Heatmap Chart",
        rows_size=2,
        cols_size=12,
        x_axis_name="xAxis",
        y_axis_name="yAxis",
    )
