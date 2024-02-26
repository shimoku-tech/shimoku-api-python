from shimoku import Client


def use_s(shimoku_client: Client):
    return shimoku_client  # error


def action(shimoku_client: Client):
    use_s(shimoku_client)
