from shimoku.cli.cloud.list import add_list_parser
from shimoku.cli.cloud.create import add_create_parser
from shimoku.cli.cloud.delete import add_delete_parser
from shimoku.cli.cloud.get import add_get_parser
from shimoku.cli.cloud.update import add_update_parser
from shimoku.cli.cloud.execute import add_execute_parser
from shimoku.cli import CLIParser
from typing import Optional


def add_cloud_parser(parser: Optional[CLIParser] = None):
    """Function to add the cloud parser to a parser
    :param parser: Parser to add the cloud parser to
    :return: Cloud parser
    """
    params = {
        "name": "cloud",
        "description": "Commands to interact with the cloud",
    }

    if parser:
        cloud_parser = parser.add_command(**params)
    else:
        cloud_parser = CLIParser(**params)

    add_list_parser(cloud_parser)
    add_get_parser(cloud_parser)
    add_create_parser(cloud_parser)
    add_delete_parser(cloud_parser)
    add_update_parser(cloud_parser)
    add_execute_parser(cloud_parser)

    return cloud_parser


if __name__ == "__main__":
    add_cloud_parser().parse_args()
