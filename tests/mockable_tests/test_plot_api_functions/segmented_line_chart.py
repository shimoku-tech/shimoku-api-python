from shimoku import Client
from .data.segmented_line import segmented_line_data


def segmented_line_chart(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "Segmented Line Chart")
    marking_lines = [0, 50, 100, 150, 200, 300]
    range_colors = ["green", "yellow", "orange", "red", "purple", "maroon"]
    x_axis_name = "Date"
    y_axis_name = "AQI"

    shimoku_client.plt.segmented_line(
        data=segmented_line_data,
        order=0,
        x="date",
        y=["y", "y_displaced", "y_multiplied"],
        marking_lines=marking_lines,
    )

    shimoku_client.plt.segmented_line(
        data=segmented_line_data,
        order=1,
        x="date",
        y="y",
        title="Beijing's Air Quality Index",
        marking_lines=marking_lines,
        range_colors=range_colors,
        x_axis_name=x_axis_name,
        y_axis_name=y_axis_name,
        variant="clean",
    )
