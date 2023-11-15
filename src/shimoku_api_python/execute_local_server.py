import subprocess
import socket
import psutil
import webbrowser
import time
import os

import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


@logging_before_and_after(logger.debug)
def check_server(server_host: str, server_port: int):
    """
    Check if the server is already running.
    :param server_host: The server host.
    :param server_port: The port where the server is running.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((server_host, server_port))
    sock.close()
    return result == 0


@logging_before_and_after(logger.debug)
def kill_server(server_host: str, server_port: int):
    """
    Kill the server process.
    """
    cmd_line = ['local_server:app', '--host', server_host, '--port', str(server_port)]

    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['cmdline'] is not None and (len(process.info['cmdline'])-2 == len(cmd_line) and
                                                    all([elm1 == elm2 for elm1, elm2 in
                                                         zip(cmd_line, process.info['cmdline'][2:])])):
            server_pid = None
            try:
                server_pid = process.info['pid']
                proc = psutil.Process(server_pid)
                proc.terminate()
                print(f"Server (PID: {server_pid}) terminated gracefully.")
            except psutil.NoSuchProcess:
                print(f"Process with PID {server_pid} not found.")


@logging_before_and_after(logger.debug)
def create_server(environment: str, server_host: str, server_port: int, open_server_browser: bool):
    """
    Create a new server process and open the server URL in the default web browser.
    :param server_host: The server host.
    :param server_port: The port where the server will run.
    :param open_server_browser: Whether to open the server URL in the default web browser.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Set the PYTHONPATH to include the directory of your FastAPI module
    env = os.environ.copy()
    env["PYTHONPATH"] = base_path + os.pathsep + env.get("PYTHONPATH", "")

    server_process = subprocess.Popen(
        ["uvicorn", "local_server:app", "--host", server_host, "--port", str(server_port)],
        env=env, stdout=subprocess.DEVNULL
    )

    print(f"Server started (PID: {server_process.pid})")

    max_time = 5
    # Wait for the server to fully initialize
    while not check_server(server_host, server_port):
        time.sleep(0.1)
        max_time -= 0.1
        if max_time <= 0:
            log_error(logger, "Server not initialized after 5 seconds.", RuntimeError)

    if open_server_browser:
        # Open the server URL in the default web browser
        webbrowser.open(f"http://{server_host}:{server_port}/graphql")

    environment_prefix = ''
    if environment != 'production':
        if environment.lower() in 'development':
            environment = 'develop'
        environment_prefix = f'{environment}.'

    webbrowser.open(f"http://{environment_prefix}shimoku.io/playground?port={server_port}")


def main():
    server_host = "127.0.0.1"
    server_port = 8000
    kill_server_flag = True
    server_running = check_server(server_host, server_port)
    if server_running:
        print("Server already running")
        if kill_server_flag:
            kill_server()
            server_running = False

    if not server_running:
        create_server(server_host, server_port, True)


if __name__ == "__main__":
    main()
