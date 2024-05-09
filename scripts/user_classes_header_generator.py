import dataclasses
import inspect
import importlib
import os
from shimoku.utils import get_args_with_defaults
import subprocess

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
target_paths = {
    os.path.join(base_path, "src", "shimoku", "api", "user_access_classes"): "*",
    os.path.join(base_path, "src", "shimoku", "ai"): "ai_layer.py",
    os.path.join(base_path, "src", "shimoku", "plt"): "plt_layer.py",
}


def handle_annotation(annotation: type) -> str:
    if hasattr(annotation, "_use_info_logging") and annotation._use_info_logging:
        return f"{annotation.__name__}Header"
    if annotation is type(None) or annotation is None:
        type_str = "None"
    elif hasattr(annotation, "__name__"):
        type_str = annotation.__name__
    else:
        type_str = str(annotation)
    return (
        type_str.replace("NoneType", "None")
        .replace("pandas.core.frame.DataFrame", " DataFrame")
        .replace("typing.", "")
        .replace("<built-in function callable>", "callable")
    )


def handle_parameter(name: str, annotation: type, default_args: dict) -> str:
    if name in default_args:
        default_value = default_args[name]
        if isinstance(default_value, str):
            default_value = f'"{default_value}"'
        return f"        {name}: {handle_annotation(annotation)} = {default_value},"
    else:
        return f"        {name}: {handle_annotation(annotation)},"


def handle_method(method) -> list[str]:
    method_code_lines = []
    method_code_lines.extend(
        [
            f"    def {method[0]}(",
            "        self,",
            *[
                handle_parameter(
                    arg,
                    method[1].__annotations__[arg],
                    get_args_with_defaults(method[1]),
                )
                for arg in method[1].__annotations__
                if arg not in ["self", "return"]
            ],
        ]
    )
    sig = inspect.signature(method[1])
    params = sig.parameters.values()
    has_kwargs = any([True for p in params if p.kind == p.VAR_KEYWORD])
    if has_kwargs:
        method_code_lines.append("        **kwargs,")
    if "return" in method[1].__annotations__:
        method_code_lines.append(
            f'    ) -> {handle_annotation(method[1].__annotations__["return"])}:'
        )
    else:
        method_code_lines.append("    ):")
    method_code_lines.extend(
        [
            f'        """{method[1].__doc__}"""',
            "        pass",
            "",
        ]
    )
    return method_code_lines


def handle_class(class_for_generation) -> list[str]:
    print(class_for_generation[0])
    is_dataclass = hasattr(class_for_generation[1], "__dataclass_fields__")

    fields_code_lines = []
    if is_dataclass:
        for field in class_for_generation[1].__dataclass_fields__.values():
            if field.default is dataclasses.MISSING:
                fields_code_lines.append(f"    {field.name}: {handle_annotation(field.type)}")
            else:
                fields_code_lines.append(
                    f"    {field.name}: {handle_annotation(field.type)} = {field.default}"
                )

    methods = inspect.getmembers(
        class_for_generation[1], predicate=inspect.isfunction
    )
    methods_code_lines = []
    for method in methods:
        if method[0].startswith("_"):
            continue
        methods_code_lines.extend(handle_method(method))

    inner_classes = inspect.getmembers(
        class_for_generation[1], predicate=inspect.isclass
    )

    inner_classes_code_lines = []
    for inner_class in inner_classes:
        if inner_class[0].startswith("_"):
            continue
        inner_classes_code_lines.extend(["    "+line for line in handle_class(inner_class)])

    if is_dataclass:
        class_header_code_lines = [
            f"@dataclass",
            f"class {class_for_generation[0]}:",
            '    """',
            *["    " + line for line in fields_code_lines],
            '    """',
        ]
    else:
        class_header_code_lines = [
            f"class {class_for_generation[0]}Header:",
            f'    """{class_for_generation[1].__doc__}"""',
            ""
        ]

    class_code_lines = [
        "",
        *class_header_code_lines,
        *fields_code_lines,
        "",
        *inner_classes_code_lines,
        *methods_code_lines,
    ]
    return class_code_lines


def main():
    for target_path, target_file in target_paths.items():
        output_path = os.path.join(target_path, "generated_headers")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for file in os.listdir(target_path):
            if file != target_file and target_file != "*":
                continue
            if file.endswith(".py") and not file.startswith("__"):
                print(
                    f'{os.path.relpath(target_path, base_path).replace(os.sep, ".")[4:]}.{file[:-3]}'
                )
                module = importlib.import_module(
                    f'{os.path.relpath(target_path, base_path).replace(os.sep, ".")[4:]}.{file[:-3]}'
                )
                classes_for_generation = []
                for name, obj in inspect.getmembers(module):
                    if not inspect.isclass(obj):
                        continue
                    if name.startswith("_"):
                        continue
                    if not hasattr(obj, "_use_info_logging") or not obj._use_info_logging:
                        continue
                    classes_for_generation.append((name, obj))

                if not classes_for_generation:
                    continue

                classes_code_lines = []
                for class_for_generation in classes_for_generation:
                    classes_code_lines.extend(handle_class(class_for_generation))

                main_code_lines = [
                    "# This file was generated automatically by "
                    "scripts/user_classes_header_generator.py do not modify it!",
                    "# If the user access files are modified, this file has to be regenerated with the script.",
                    "from typing import Optional, Union",
                    "from pandas import DataFrame",
                    "from dataclasses import dataclass",
                    "import shimoku",
                    "",
                    *classes_code_lines,
                ]
                with open(
                    os.path.join(output_path, f"{classes_for_generation[-1][0]}Header.py"),
                    "w",
                ) as f:
                    f.write("\n".join(main_code_lines))

                subprocess.run(
                    [
                        "black",
                        os.path.join(
                            output_path, f"{classes_for_generation[-1][0]}Header.py"
                        ),
                    ]
                )


if __name__ == "__main__":
    main()
