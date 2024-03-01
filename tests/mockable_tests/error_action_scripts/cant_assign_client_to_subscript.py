from shimoku import Client


class UsesClient:
    clients_dict = {}

    def assign_s(self, shimoku_client: Client):
        self.clients_dict["s"] = shimoku_client  # error


def action(shimoku_client: Client):
    uses_shimoku_client = UsesClient()
    uses_shimoku_client.assign_s(shimoku_client)
