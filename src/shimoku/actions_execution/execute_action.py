import uuid
import ast
from typing import Dict, Optional
from shimoku.utils import IN_BROWSER
from shimoku.exceptions import ActionError
from shimoku.execution_logger import log_error
import warnings

import logging

logger = logging.getLogger(__name__)


class Scope:
    def __init__(self, parent_scope: Optional["Scope"] = None):
        self.lines_need_async = set()
        self.inner_scopes: Dict[str, Scope] = {}
        self.needs_async = False
        self.parent_scope: Optional[Scope] = parent_scope
        self.parameters: dict = {}

    def get_function(self, name: str):
        if name in self.inner_scopes:
            return self.inner_scopes[name]
        if self.parent_scope is not None:
            return self.parent_scope.get_function(name)
        return None

    def user_defined_scope(self):
        return (
            self.parent_scope is not None and self.parent_scope.parent_scope is not None
        )

    def enter_scope(self, name: str):
        if name not in self.inner_scopes:
            self.inner_scopes[name] = Scope(self)
        return self.inner_scopes[name]

    def exit_scope(self):
        return self.parent_scope


class ActionsChecker(ast.NodeVisitor):
    shimoku_client_attrs = [
        "universes",
        "workspaces",
        "boards",
        "menu_paths",
        "components",
        "data",
        "io",
        "activities",
        "plt",
        "set_workspace",
        "set_board",
        "set_menu_path",
        "run",
    ]

    SHIMOKU_CLIENT_NAME = "shimoku_client"

    def __init__(self):
        self.current_scope = Scope()
        self.in_class = False
        self.exists_action_function = False
        self.parameters = {}
        self.client_assigned = False
        self.shimoku_imported = False

    def is_shimoku_client(self, node):
        if isinstance(node, ast.Name) and node.id == self.SHIMOKU_CLIENT_NAME:
            return True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "Client"
        ):
            return True
        return False

    def visit_Import(self, node):
        if not self.current_scope.parent_scope:
            return
        for alias in node.names:
            if "asyncio" in alias.name:
                log_error(logger, "Cannot import asyncio module.", ActionError)

    def visit_ImportFrom(self, node):
        if node.module == "shimoku":
            if any(
                asname is not None for asname in [alias.asname for alias in node.names]
            ):
                log_error(
                    logger, "Cannot import shimoku modules with renaming.", ActionError
                )
            for alias in node.names:
                if alias.name == "Client":
                    self.shimoku_imported = True
        if not self.current_scope.parent_scope:
            return
        if node.module == "asyncio":
            log_error(logger, "Cannot import from asyncio module.", ActionError)

    def visit_Assign(self, node):
        for target in node.targets:
            if self.is_shimoku_client(node.value):
                if self.client_assigned:
                    log_error(logger, "Cannot assign Client instance", ActionError)
                self.client_assigned = True
            elif isinstance(target, ast.Name):
                if target.id == self.SHIMOKU_CLIENT_NAME:
                    log_error(
                        logger,
                        f"Cannot assign to {self.SHIMOKU_CLIENT_NAME} variable.",
                        ActionError,
                    )

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name == "action":
            if self.in_class:
                log_error(
                    logger,
                    "Cannot define action function inside a class.",
                    ActionError,
                )
            if self.current_scope.user_defined_scope():
                log_error(
                    logger,
                    "Cannot define action function inside another function.",
                    ActionError,
                )
            if self.exists_action_function:
                log_error(
                    logger, "Cannot define more than one action function.", ActionError
                )
            if len(node.args.args) != 1:
                log_error(
                    logger,
                    "Action function must have exactly one parameter.",
                    ActionError,
                )
            if node.args.args[0].arg != self.SHIMOKU_CLIENT_NAME:
                log_error(
                    logger,
                    "Action function parameter must be named 'shimoku_client'.",
                    ActionError,
                )
            if (
                node.args.args[0].annotation
                and node.args.args[0].annotation.id != "Client"
            ):
                log_error(
                    logger,
                    "Action function parameter must be annotated with 'Client'.",
                    ActionError,
                )
            self.exists_action_function = True

        self.current_scope = self.current_scope.enter_scope(node.name)
        self.generic_visit(node)

        for arg in node.args.args:
            if self.in_class and arg.arg == "self":
                continue

            if not arg.annotation:
                log_error(
                    logger,
                    "Annotations are mandatory for function parameters.",
                    ActionError,
                )
            if isinstance(arg.annotation, ast.Subscript):
                if "Client" in ast.dump(arg.annotation):
                    log_error(
                        logger,
                        "Cannot use Client instance as a "
                        "part of a parameter type, use 'Client' instead.",
                        ActionError,
                    )
            elif arg.annotation.id == "Client":
                if arg.arg != self.SHIMOKU_CLIENT_NAME:
                    log_error(
                        logger,
                        f"Client parameter must be named '{self.SHIMOKU_CLIENT_NAME}' not '{arg.arg}'.",
                        ActionError,
                    )
            elif arg.arg == self.SHIMOKU_CLIENT_NAME:
                log_error(
                    logger,
                    f"{self.SHIMOKU_CLIENT_NAME} parameter must be annotated with "
                    f"'Client' not '{arg.annotation.id}'.",
                    ActionError,
                )
            self.current_scope.parameters[arg.arg] = arg.annotation.id

        self.current_scope = self.current_scope.exit_scope()

    def visit_AsyncFunctionDef(self, node):
        if not self.current_scope.parent_scope:
            self.current_scope = self.current_scope.enter_scope(node.name)
            self.generic_visit(node)
            self.current_scope = self.current_scope.exit_scope()
        else:
            log_error(logger, "Cannot use async functions.", ActionError)

    def visit_ClassDef(self, node):
        self.in_class = True
        self.generic_visit(node)
        self.in_class = False

    def visit_Return(self, node):
        if isinstance(node.value, ast.Name):
            if node.value.id == self.SHIMOKU_CLIENT_NAME:
                log_error(
                    logger,
                    f"Cannot return Client instance '{node.value.id}'.",
                    ActionError,
                )
        self.generic_visit(node)

    def visit_Call(self, node):
        self.generic_visit(node)

        # Check if the call is a method call that requires await
        if isinstance(node.func, ast.Attribute):
            aux_node = node.func
            while not isinstance(aux_node.value, ast.Name):
                if not isinstance(aux_node.value, ast.Attribute):
                    return
                aux_node = aux_node.value
            if (
                aux_node.value.id == self.SHIMOKU_CLIENT_NAME
                and aux_node.attr in self.shimoku_client_attrs
            ):
                # print(
                #     f"Client method call '{node.func.attr}' used at line {node.lineno} without await."
                # )
                self.current_scope.lines_need_async.add((node.lineno, node.col_offset))
                self.current_scope.needs_async = True

        if (
            not isinstance(node.func, ast.Name)
            or self.current_scope.get_function(node.func.id) is None
        ):
            return

        function_scope = self.current_scope.get_function(node.func.id)
        if function_scope.needs_async:
            self.current_scope.needs_async = True

        parameters = function_scope.parameters
        parameter_types = list(parameters.values())
        for i, arg in enumerate(node.args):
            if self.is_shimoku_client(arg) and not parameter_types[i] == "Client":
                log_error(
                    logger,
                    f"The value asigned to the parameter '{arg.id}' is the Client, "
                    f"but the function '{node.func.id}' expects a '{parameter_types[i]}' instance.",
                    ActionError,
                )
        for keyword in node.keywords:
            if (
                self.is_shimoku_client(keyword.value)
                and not parameters[keyword.arg] == "Client"
            ):
                log_error(
                    logger,
                    f"The value asigned to the parameter '{keyword.arg}' is the Client, "
                    f"but the function '{node.func.id}' expects a '{parameters[keyword.arg]}' instance.",
                    ActionError,
                )


class AwaitInserter(ast.NodeTransformer):
    def __init__(self, scope: Scope):
        self.current_scope = scope

    def visit_Call(self, node):
        self.generic_visit(node)
        if not self.current_scope.parent_scope:
            return node

        if (node.lineno, node.col_offset) in self.current_scope.lines_need_async:
            self.current_scope.needs_async = True
            return ast.copy_location(ast.Await(value=node), node)

        # Check if the call is a function call that requires await
        func_name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        function_scope = self.current_scope.get_function(func_name)
        if function_scope is not None and function_scope.needs_async:
            self.current_scope.needs_async = True
            # print(
            #     f"Function call '{func_name}' used at line {node.lineno} without await."
            # )
            return ast.copy_location(ast.Await(value=node), node)

        return node

    def visit_FunctionDef(self, node):
        self.current_scope = self.current_scope.enter_scope(node.name)
        node = self.generic_visit(node)
        async_node = None
        if self.current_scope.needs_async:
            # Convert to an async function
            async_node = ast.AsyncFunctionDef(
                name=node.name,
                args=node.args,
                body=node.body,
                decorator_list=node.decorator_list,
                returns=node.returns,
                type_comment=node.type_comment,
            )
        self.current_scope = self.current_scope.exit_scope()
        if async_node is not None:
            return ast.copy_location(async_node, node)
        return node

    def visit_AsyncFunctionDef(self, node):
        self.current_scope = self.current_scope.enter_scope(node.name)
        node = self.generic_visit(node)
        self.current_scope = self.current_scope.exit_scope()
        return node


def print_code_with_line_numbers(code: str):
    code_lines = code.split("\n")
    for i, line in enumerate(code_lines):
        print(f"{i:3} | {line}")


def analyze_action_code(
    code: str,
    print_code: bool = False,
) -> ast.Module:
    code = code.replace("\r\n", "\n").replace("\\\n", "").replace("\\\r", "")
    code_lines = code.split("\n")
    main_uuid = str(uuid.uuid4()).replace("-", "_")

    script_code_lines = [
        "import asyncio",
        "from shimoku.actions_execution.front_connection import global_front_end_connection",
        "",
        "global_front_end_connection.js_snackbar = js_snackbar",
        "",
        f"async def main_{main_uuid}():",
        *[f"    {line}" for line in code_lines],
        "    shimoku_client = Client(",
        "        access_token=js_access_token,",
        "        universe_id=js_universe_id,",
        "        environment=js_environment,",
        "        async_execution=True,",
        "        verbosity='INFO',",
        "        retry_attempts=1"
        "    )",
        "    shimoku_client.set_workspace(js_workspace_id)",
        "    action(shimoku_client)",
        "",
    ]
    if IN_BROWSER:
        script_code_lines.append(
            f"asyncio.get_event_loop().create_task(main_{main_uuid}())",
        )
    else:
        script_code_lines.insert(
            -3, "    shimoku_client._async_pool.ACTIONS_TEST = True"
        )
        script_code_lines.append(
            f"asyncio.run(main_{main_uuid}())",
        )

    if print_code:
        for i, line in enumerate(script_code_lines):
            print(f"{i:3} | {line}")
    try:
        script_ast = ast.parse("\n".join(script_code_lines))
        analyzer = ActionsChecker()
        analyzer.visit(script_ast)
        if not analyzer.exists_action_function:
            log_error(logger, "Action function is not defined.", ActionError)
        if not analyzer.shimoku_imported:
            log_error(logger, "Shimoku's Client is not imported.", ActionError)
        modifier = AwaitInserter(analyzer.current_scope)
        modifier.visit(script_ast)
    except Exception as e:
        print_code_with_line_numbers("\n".join(script_code_lines))
        log_error(logger, f"Error while analyzing the code: {e}", ActionError)
        raise e
    return script_ast


def execute_action_code(
    code: str,
    print_code: bool = False,
    js_access_token: str = None,
    js_universe_id: str = "local",
    js_environment: str = "production",
    js_workspace_id: str = "local",
    js_snackbar: Optional[callable] = None
):
    context = {
        'js_access_token': js_access_token,
        'js_universe_id': js_universe_id,
        'js_environment': js_environment,
        'js_workspace_id': js_workspace_id,
        'js_snackbar': js_snackbar,
    }
    script_ast = analyze_action_code(code, print_code)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    exec(compile(script_ast, filename="shimoku_action", mode="exec"), context)
    warnings.resetwarnings()


def main():
    # with open('../../../tests/mockable_tests/test_plot_api.py', 'r') as f:
    with open("../../../tests/personal_test.py", "r") as f:
        code_lines = f.readlines()
    execute_action_code("\n".join(code_lines))


if __name__ == "__main__":
    main()
