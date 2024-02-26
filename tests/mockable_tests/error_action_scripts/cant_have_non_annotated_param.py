from shimoku import Client


def use_s(non_annotated_param):  # error
    pass


def action(shimoku_client: Client):
    use_s(shimoku_client)
