from shimoku import Client


class UsesClient:
    s = Client()  # error

    def use_s(self):
        pass


def action(shimoku_client: Client):
    pass
