from shimoku.cli import CLIParser
import webbrowser
from typing import Optional
from multiprocessing import Process
import psutil


def add_playground_parser(parser: Optional[CLIParser] = None):
    """
    Function to add the playground parser to a parser
    :param parser: Parser to add the playground parser to
    """

    params = {
        "name": "playground",
        "description": "Commands to interact with the playground",
    }

    if parser:
        playground_parser = parser.add_command(**params)
    else:
        playground_parser = CLIParser(**params)

    module_functions = [init, terminate]

    for func in module_functions:
        playground_parser.decor_add_command()(func)

    return playground_parser


def init(local_port: Optional[int], env: Optional[str]):
    """Start the playground server
    :param local_port: Port to use for the server
    :param env: Environment to use in the browser
    """
    from shimoku.playground.local_server import main

    if not local_port:
        local_port = 8000
    environment_prefix = f"{env}." if env and env != "production" else ""
    webbrowser.open(
        f"http://{environment_prefix}shimoku.io/playground?port={local_port}"
    )
    proc = Process(
        target=main,
        args=(
            None,
            local_port,
        ),
    )
    try:
        proc.start()
        proc.join()
    except KeyboardInterrupt:
        proc.terminate()
        print("Server terminated.")


def terminate(local_port: Optional[int]):
    """Terminate the playground server (for servers running on the background)
    :param local_port: Port to use for the server
    """
    if local_port is None:
        local_port = 8000
    cmd_lines = [
        ["local_server:app", "--host", "127.0.0.1", "--port", str(local_port)],
        ["playground", "init"],
    ]

    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        if process.info["cmdline"] is not None and any(
            [
                all([elm in process.info["cmdline"] for elm in cmd_line])
                for cmd_line in cmd_lines
            ]
        ):
            try:
                server_pid = process.info["pid"]
                proc = psutil.Process(server_pid)
                proc.terminate()
                print(f"Server (PID: {server_pid}) terminated gracefully.")
            except psutil.NoSuchProcess:
                print(f"Process with PID {server_pid} not found.")
