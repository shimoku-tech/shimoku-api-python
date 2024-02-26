from shimoku import Client


async def use_s(shimoku_client: Client):  # error
    pass


def action(shimoku_client: Client):
    use_s(shimoku_client)
