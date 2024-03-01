from shimoku import Client
from .data.line_with_confidence_area import confidence_data


def line_with_confidence_area(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "Line with confidence area")

    shimoku_client.plt.line_with_confidence_area(
        data=confidence_data,
        order=0,
        title="Confidence Band Chart",
        x="date",
        y="value",
        lower="l",
        upper="u",
        x_axis_name="Date",
        y_axis_name="Value",
        percentages=True,
        variant="clean",
    )
