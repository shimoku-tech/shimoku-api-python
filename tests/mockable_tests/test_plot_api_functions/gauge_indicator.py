from shimoku import Client


def gauge_indicators(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "gauge-indicator")

    shimoku_client.plt.gauge_indicator(
        order=0,
        value=83,
        description="Síntomas coincidientes | Mareo, Dolor cervical",
        title="Sobrecarga muscular en cervicales y espalda",
    )

    shimoku_client.plt.gauge_indicator(
        order=2,
        value=31,
        color=2,
        description="Síntomas coincidientes | Dolor cervical",
        title="Bruxismo",
    )
