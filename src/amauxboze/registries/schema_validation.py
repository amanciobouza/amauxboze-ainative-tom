from __future__ import annotations

from typing import Any


class SchemaValidationError(ValueError):
    pass


def _type_matches(value: Any, expected: str) -> bool:
    mapping = {
        "string": str,
        "array": list,
        "object": dict,
        "boolean": bool,
        "number": (int, float),
        "integer": int,
    }
    py_type = mapping.get(expected)
    if py_type is None:
        return True
    if expected == "integer" and isinstance(value, bool):
        return False
    if expected == "number" and isinstance(value, bool):
        return False
    return isinstance(value, py_type)


def validate_against_schema(data: dict[str, Any], schema: dict[str, Any], *, label: str) -> None:
    if schema.get("type") == "object" and not isinstance(data, dict):
        raise SchemaValidationError(f"{label} must be an object")

    for field in schema.get("required", []):
        if field not in data:
            raise SchemaValidationError(f"{label} missing required field: {field}")

    properties = schema.get("properties", {})
    for key, value in data.items():
        rule = properties.get(key)
        if not rule:
            continue
        expected = rule.get("type")
        if expected and not _type_matches(value, expected):
            raise SchemaValidationError(
                f"{label}.{key} must be of type {expected}"
            )
        if expected == "array" and isinstance(value, list):
            item_rule = rule.get("items", {})
            item_type = item_rule.get("type")
            if item_type:
                for index, item in enumerate(value):
                    if not _type_matches(item, item_type):
                        raise SchemaValidationError(
                            f"{label}.{key}[{index}] must be of type {item_type}"
                        )
