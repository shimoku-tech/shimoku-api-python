from shimoku import Client


def use_s(other_param: int):
    print(other_param)


def action(shimoku_client: Client):
    use_s(shimoku_client)  # error
