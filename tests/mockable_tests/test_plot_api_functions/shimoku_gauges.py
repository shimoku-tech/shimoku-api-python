import pandas as pd
from os import path
from shimoku import Client

data_path = path.join(path.dirname(path.abspath(__file__)), "data")


def shimoku_gauges(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "shimoku-gauges")
    df = pd.read_csv(path.join(data_path, "test_stack_distribution.csv"))

    value_columns = [col for col in df.columns if col != "Segment"]
    df = df[["Segment"] + value_columns]

    gauges_data = pd.DataFrame(columns=["name", "value", "color"])
    df_transposed = df.transpose().reset_index().drop(0)
    value_columns = [col for col in df_transposed.columns if col != "index"]
    gauges_data["value"] = df_transposed[value_columns].apply(
        lambda row: sum(row), axis=1
    )
    gauges_data["name"] = df_transposed["index"]
    gauges_data["color"] = range(1, len(df_transposed) + 1)

    order = shimoku_client.plt.shimoku_gauges_group(
        gauges_data=gauges_data,
        order=0,
        cols_size=12,
        rows_size=3,
        calculate_percentages=True,
    )

    shimoku_client.plt.shimoku_gauge(value=-60, order=order, color=1)

    order += 1
    shimoku_client.plt.shimoku_gauge(
        value=60, order=order, name="test", color="status-error"
    )

    order += 1
    shimoku_client.plt.shimoku_gauge(
        value=-90, order=order, name="test", color="#FF0000"
    )
