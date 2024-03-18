from shimoku.actions_execution.execute_action import execute_action_code
from shimoku.exceptions import ActionError, CacheError
from utils import initiate_shimoku
from os import path, listdir
import unittest

correct_scripts_path = path.join(path.dirname(__file__), "correct_action_scripts")
error_scripts_path = path.join(path.dirname(__file__), "error_action_scripts")


class TestActions(unittest.TestCase):
    def test_action_execute(self):
        for correct_action_script in listdir(correct_scripts_path):
            execute_action_code(
                open(path.join(correct_scripts_path, correct_action_script)).read(),
                True,
            )

        for code_with_errors in listdir(error_scripts_path):
            print()
            with self.assertRaises(ActionError):
                execute_action_code(code_with_errors, True)

    def test_create_action(self):
        correct_action_script = path.join(correct_scripts_path, "correct_action.py")
        code = open(correct_action_script).read()
        shimoku_client = initiate_shimoku()
        shimoku_client.actions.create_action(
            "test action",
            "test action description",
            code=code,
            overwrite=True,
            libraries=["pandas==1.5.3"],
        )
        with self.assertRaises(CacheError):
            shimoku_client.actions.create_action(
                "test action",
                "test action description",
                code=code,
                overwrite=False,
                libraries=["pandas==1.5.3"],
            )
        action_metadata = shimoku_client.actions.get_action_metadata(name="test action")

        assert shimoku_client.actions.get_action_code(name="test action") == code
        assert action_metadata["description"] == "test action description"
        assert action_metadata["name"] == "test action"
        assert action_metadata["pythonLibraries"] == ["pandas==1.5.3"]

        shimoku_client.actions.delete_action(name="test action")

        with self.assertRaises(ActionError):
            shimoku_client.actions.get_action_metadata(name="test action")
