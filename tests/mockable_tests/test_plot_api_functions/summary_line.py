from shimoku import Client
from .data.summary_line import summary_data


def summary_line(shimoku_client: Client):
    shimoku_client.set_menu_path("test-bentobox", "summary-line")

    shimoku_client.plt.line_with_summary(
        data=summary_data,
        order=4,
        x="date",
        y="x",
        title="Total",
        description="Today",
        value=7.94,
    )
