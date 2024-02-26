from shimoku import Client


def iframe(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "iframe-test")
    url = "https://www.marca.com/"
    shimoku_client.plt.iframe(url=url, order=0)
    shimoku_client.plt.iframe(
        url=url, order=1, height=160 * 8, cols_size=6, padding="0,3,0,3"
    )
