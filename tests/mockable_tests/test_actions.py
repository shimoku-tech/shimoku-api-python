from shimoku.actions.execute_action import execute_action
from shimoku.exceptions import ActionError
from os import path, listdir
import unittest

correct_scripts_path = path.join(path.dirname(__file__), "correct_action_scripts")
error_scripts_path = path.join(path.dirname(__file__), "error_action_scripts")


class TestActions(unittest.TestCase):
    def test_action(self):
        for correct_action_script in listdir(correct_scripts_path):
            execute_action(
                open(path.join(correct_scripts_path, correct_action_script)).read(),
                True,
            )

        for code_with_errors in listdir(error_scripts_path):
            print()
            with self.assertRaises(ActionError):
                execute_action(code_with_errors, True)
