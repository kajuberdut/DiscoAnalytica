from typing import Any, Callable, get_type_hints

from discoanalytica.utility.better_default_dict import BetterDefaultDict as defaultdict


def recursive_defaultdict():
    """Creates a recursively nested defaultdict."""
    return defaultdict(recursive_defaultdict)


class DotMapper:
    _store = None

    def __init__(self):
        if self._store is None:
            self._store = recursive_defaultdict()

    def __setitem__(self, key: str, value: Callable[[Any, dict], None]):
        """
        Sets a value in the nested dictionary structure using a dot-separated key.
        Ensures that terminal values are callables accepting (data_definition, step).

        Example:
            dm["a.b.c"] = some_callable
        """
        if not callable(value):
            raise ValueError(
                "Terminal values must be callable and accept (data_definition, step) arguments."
            )

        hints = get_type_hints(value)
        expected_args = ["data_definition", "step"]
        if list(hints.keys())[:2] != expected_args:
            raise ValueError(
                f"Callable must have parameters {expected_args}, but got {list(hints.keys())}"
            )

        parts = key.split(".")
        d = self._store
        for part in parts[:-1]:
            d = d[part]  # defaultdict auto-creates missing keys
        d[parts[-1]] = value

    def __getitem__(self, key):
        """
        Retrieves the value stored at a dot-separated key.

        Example:
            dm["a.b"] -> returns a plain dict.
        """
        parts = key.split(".")
        d = self._store
        for part in parts:
            d = d[part]
        return d
