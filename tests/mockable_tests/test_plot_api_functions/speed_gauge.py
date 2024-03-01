from shimoku import Client


def speed_gauge(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "speed-gauge-test")

    shimoku_client.plt.speed_gauge(
        name="Third", value=60, min_value=0, max_value=70, order=0
    )
