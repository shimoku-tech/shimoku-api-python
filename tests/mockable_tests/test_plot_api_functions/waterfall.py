from shimoku import Client
from .data.waterfall import waterfall_data
from .data.random_waterfall import random_waterfall_data


def waterfall(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "waterfall-test")

    shimoku_client.plt.waterfall(
        data=waterfall_data,
        x="x",
        positive="income",
        negative="expenses",
        order=0,
        variant="minimal",
    )

    shimoku_client.plt.waterfall(
        data=waterfall_data,
        x="x",
        title="Waterfall with balance",
        positive="income",
        negative="expenses",
        show_balance=True,
        order=1,
    )

    shimoku_client.update_data_sets()
    shimoku_client.plt.waterfall(
        data=random_waterfall_data,
        x="x",
        title="Big random waterfall",
        positive="Income",
        negative="Expenses",
        x_axis_name="Day",
        y_axis_name="Money in €",
        show_balance=True,
        order=2,
        variant="clean",
    )
    shimoku_client.reuse_data_sets()
