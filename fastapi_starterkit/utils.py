from typing import Any, TypeVar


def validate_type_arg(type_arg: Any, expected_type: Any = None):
    if type(type_arg) == TypeVar:
        raise ValueError("Missing type")
    if expected_type is not None and not issubclass(type_arg, expected_type):
        raise ValueError(f"Model type {type_arg} is not {expected_type.__module__}.{expected_type.__name__}")
