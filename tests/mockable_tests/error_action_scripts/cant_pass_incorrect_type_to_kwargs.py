from shimoku import Client


def use_s(other_param: int):
    pass


def action(shimoku_client: Client):
    use_s(other_param=shimoku_client)  # error
