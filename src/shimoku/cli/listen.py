from shimoku.cli import CLIParser, CLIFuncParam
from typing import Optional
from shimoku.exceptions import ActionError
from shimoku.actions_execution.execute_action import execute_action_code
import time
import subprocess
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ast

import logging

logger = logging.getLogger(__name__)


def add_listener_parser(parser: Optional[CLIParser] = None):
    """
    Function to add the listener parser to a parser
    :param parser: Parser to add the listener parser to
    """

    params = {
        "name": "listen",
        "description": "Commands to execute continuously a file by listening to changes",
    }

    if parser:
        listener_parser = parser.add_command(**params)
    else:
        listener_parser = CLIParser(**params)

    common_args = [
        CLIFuncParam(
            name="path_to_code",
            arg_help="Path to the file to be listened to",
            arg_type=str,
            is_path=True,
            prompt=True,
        )
    ]

    module_functions = [script, action]

    for func in module_functions:
        listener_parser.decor_add_command(common_args=common_args)(func)

    return listener_parser


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, script_path, is_action=False):
        self.script_path = script_path
        self.is_action = is_action
        self.last_content = None

    def on_modified(self, event):
        if event.src_path == self.script_path:
            print(f"Detected change in file: {self.script_path}")
            self.process_file()

    def process_file(self):
        try:
            with open(self.script_path, "r") as file:
                current_content = file.read()

            if current_content == self.last_content:
                print("File content unchanged, ignoring event.")
                return

            self.last_content = current_content
            ast.parse(current_content)  # Check for syntax errors

            if not self.is_action:
                self.execute_script()
            else:
                self.execute_action()

        except SyntaxError as e:
            print("Could not execute file, syntax error:", e)
        except subprocess.CalledProcessError as e:
            print("Could not execute file:", e)
        except Exception as e:
            print(f"Error processing file: {e}")

    def execute_script(self):
        subprocess.run(f"python {self.script_path}", check=True, shell=True)
        print("Script executed successfully")

    def execute_action(self):
        thread = threading.Thread(target=execute_action_code, args=(self.last_content,))
        thread.start()
        thread.join()
        print("Action executed successfully")


def script(**kwargs):
    """
    Function to listen to changes in a script
    """
    path_to_code = kwargs["path_to_code"]
    event_handler = FileChangeHandler(path_to_code)
    observer = Observer()
    observer.schedule(event_handler, path=path_to_code, recursive=False)
    observer.start()
    print("Watching for file changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def action(**kwargs):
    """
    Function to listen to changes in an action
    """
    path_to_code = kwargs["path_to_code"]
    event_handler = FileChangeHandler(path_to_code, is_action=True)
    observer = Observer()
    observer.schedule(event_handler, path=path_to_code, recursive=False)
    observer.start()
    print("Watching for file changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
