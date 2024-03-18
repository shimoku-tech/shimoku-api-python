from shimoku import Client


class UsesClient:
    def __init__(self):
        print("This should work")

    def use_s(self, shimoku_client: Client):
        shimoku_client.set_workspace()
        shimoku_client.set_menu_path("Pyodide test")
        shimoku_client.plt.gauge_indicator(
            order=2,
            value=len(
                shimoku_client.menu_paths.get_menu_path_components(
                    name="test-free-echarts"
                )
            ),
            description="Trying to get the number of components",
            title="Pyodide test",
        )


def deep_no_use_s(shimoku_client: Client):
    pass


def no_use_s(shimoku_client: Client):
    deep_no_use_s(shimoku_client)


def deep_deep_use_s(shimoku_client: Client):
    shimoku_client.set_workspace()
    shimoku_client.set_menu_path("Pyodide test")
    shimoku_client.plt.gauge_indicator(
        order=1,
        value=len(
            shimoku_client.menu_paths.get_menu_path_components(name="test-free-echarts")
        ),
        description="Trying to get the number of components",
        title="Pyodide test",
    )


def use_s(shimoku_client: Client):
    def deep_use_s():
        deep_deep_use_s(shimoku_client)

    deep_use_s()


def action(shimoku_client: Client):
    shimoku_client._async_pool.ACTIONS_TEST = True
    print("This should work")
    no_use_s(shimoku_client)
    use_s(shimoku_client)

    uses_shimoku_client = UsesClient()
    uses_shimoku_client.use_s(shimoku_client)

    shimoku_client.run()
