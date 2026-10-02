"""Reject ambiguous, nonstandard, or excessively nested JSON input."""

import json


def loads(text: str):
    def object_pairs(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate JSON key")
            value[key] = item
        return value

    def constant(value):
        raise ValueError("nonstandard JSON number")

    try:
        value = json.loads(text, object_pairs_hook=object_pairs, parse_constant=constant)
        pending = [(value, 0)]
        while pending:
            item, depth = pending.pop()
            if isinstance(item, (dict, list)):
                if depth >= 128:
                    raise ValueError("JSON nesting exceeds the limit")
                children = item.values() if isinstance(item, dict) else item
                pending.extend((child, depth + 1) for child in children)
        return value
    except (ValueError, RecursionError) as exc:
        raise ValueError("invalid or ambiguous JSON") from exc
