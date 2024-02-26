import pandas as pd
from shimoku import Client
from .data.bar_and_line import bar_and_line_data


def bar_and_line_chart(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "Bar and line chart")

    shimoku_client.plt.line_and_bar_charts(
        data=bar_and_line_data,
        order=0,
        x="day",
        bar_names=["Evaporation", "Precipitation"],
        line_names=["Temperature"],
        title="rainfall and temperature",
        x_axis_name="Day",
        line_axis_name="Temperature",
        line_suffix=" °C",
        bar_axis_name="Evaporation and precipitacion",
        bar_suffix=" ml",
        variant="minimal",
    )

    aux_data = pd.DataFrame(bar_and_line_data)

    aux_data["Temperature"] = aux_data["Temperature"] * 67
    aux_data["Evaporation"] = aux_data["Evaporation"] * 42
    aux_data["Precipitation"] = aux_data["Precipitation"] * 42

    shimoku_client.plt.line_and_bar_charts(
        data=aux_data,
        order=1,
        x="day",
        bar_names=["Evaporation", "Precipitation"],
        line_names=["Temperature"],
        title="rainfall and temperature",
        x_axis_name="Day",
        line_axis_name="Temperature",
        line_suffix=" °C",
        bar_axis_name="Evaporation and precipitacion",
        bar_suffix=" ml",
        variant="clean",
    )

    aux_data = pd.DataFrame(bar_and_line_data)

    aux_data["Temperature"] = aux_data["Temperature"] / 10000
    aux_data["Evaporation"] = aux_data["Evaporation"] * 542
    aux_data["Precipitation"] = aux_data["Precipitation"] * 542

    shimoku_client.plt.line_and_bar_charts(
        data=aux_data,
        order=2,
        x="day",
        bar_names=["Evaporation", "Precipitation"],
        line_names=["Temperature"],
        title="rainfall and temperature",
        x_axis_name="Day",
        line_axis_name="Temperature",
        line_suffix=" °C",
        bar_axis_name="Evaporation and precipitacion",
        bar_suffix=" ml",
    )
