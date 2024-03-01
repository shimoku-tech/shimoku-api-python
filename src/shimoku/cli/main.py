from shimoku.cli.configuration import add_configuration_parser
from shimoku.cli.cloud_parser import add_cloud_parser
from shimoku.cli.playground import add_playground_parser
from shimoku.cli.persistence import add_persistence_parser
from shimoku.cli.listen import add_listener_parser
from shimoku.cli import CLIParser, CLIFuncParam

from shimoku.execution_logger import configure_logging

import asyncio

main_parser = CLIParser(
    arguments=[
        CLIFuncParam(
            name="interactive",
            arg_help="Run in interactive mode",
            mandatory=False,
            default=False,
            action="store_true",
            alt_name="i",
        ),
        CLIFuncParam(
            name="shell-commands-enabled",
            arg_help="Enable the possibility to run shell commands from the interactive mode",
            mandatory=False,
            default=False,
            action="store_true",
            alt_name="s",
        ),
    ]
)

add_configuration_parser(main_parser)
add_playground_parser(main_parser)
add_cloud_parser(main_parser)
add_persistence_parser(main_parser)
add_listener_parser(main_parser)


def main():
    configure_logging("INFO")
    try:
        asyncio.run(main_parser.parse_args())
    except KeyboardInterrupt:
        print("Interrupted by user")
    except asyncio.CancelledError:
        print("Interrupted by user")


if __name__ == "__main__":
    main()
