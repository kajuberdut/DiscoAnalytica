from collections import defaultdict
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any, Callable, Union

import yaml
from duckdb.duckdb import DuckDBPyConnection

from discoanalytica.errors import DataDefinitionError
from discoanalytica.utility.dot_mapper import DotMapper
from discoanalytica.utility.import_all import import_all_modules


class DataDefinition:
    _handlers = DotMapper()
    _loaded = False

    def __init__(
        self,
        name: str,
        license: str,
        attribution: str = "",
        steps: list = None,
        metadata: dict = None,
        file_path: Path = None,
    ):
        self.metadata = metadata or {}
        self["name"] = name
        self["license"] = license
        self["attribution"] = attribution

        self.steps = steps or []
        self.file_path = file_path

        # These packages all must be imported in order to be added to _handlers
        if self._loaded is False:
            import_all_modules("discoanalytica.step")

    @property
    def file_path(self) -> Path:
        """Getter for file_path."""
        return self._file_path

    @file_path.setter
    def file_path(self, value: Union[str, Path, None]):
        """Setter for file_path that ensures it is always stored as a Path."""
        if value is None:
            self._file_path = None
        else:
            fp = Path(value)
            if not fp.exists():
                raise ValueError("File path is not a valid path.")
            self._file_path = fp

    def __setitem__(self, key: str, value: Any):
        """
        Overrides __setitem__ to store non-dot-path values in metadata.
        """
        if (
            "." not in key
            and not isinstance(value, (dict, defaultdict))
            and not callable(value)
        ):
            self.metadata[key] = value
        else:
            DataDefinition._handlers[key] = value

    def __getitem__(self, key):
        """
        Overrides __getitem__ to check metadata first before looking in _store.
        """
        if key in self.metadata:
            return self.metadata[key]
        return DataDefinition._handlers[key]

    def __call__(self, dot_path: str, step: dict):
        """
        Calls the corresponding handler at the specified dot-separated path.
        """
        d = DataDefinition._handlers[dot_path]

        if not callable(d):
            raise ValueError(f"No callable found at path: {dot_path}")

        return d(self, step)

    @classmethod
    def from_yaml_file(cls, yaml_file: Path) -> "DataDefinition":
        """
        Load a DataDefinition instance from a YAML file.

        Args:
            yaml_file (Path): The path to the YAML file.

        Returns:
            DataDefinition: The loaded DataDefinition instance.
        """
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        return cls(**data, **{"name": yaml_file.stem})

    def process_steps(self):
        """
        Iterates over steps and dispatches them to the appropriate handlers.
        """
        for step in self.steps:
            self(step["type"], step)

    @classmethod
    def register_handler(cls, dot_path: str, handler: Callable):
        """
        Registers a definition handler function at the given dot-separated path.
        """
        cls._handlers[dot_path] = handler


def register_definition_handler(dot_path: str):
    """
    Decorator to register a handler function for a given dot path.
    """
    print(f"registering handler for {dot_path}")

    def decorator(func):
        DataDefinition.register_handler(dot_path, func)
        return func

    return decorator


def pick_data_definition() -> DataDefinition:
    """
    Presents a numbered list of .yaml files from the
    discoanalytica.data_definition.data_definitions package, allows the user to pick one,
    and returns a DataDefinition object from the chosen file.

    Raises:
        DataDefinitionError: If the data_definitions package cannot be accessed
                         or if no yaml files are found.
    """
    try:
        data_dir = files("discoanalytica.data_definition.data_definitions")
    except Exception as e:
        raise DataDefinitionError(
            f"Error accessing discoanalytica.data_definition.data_definitions: {e}"
        ) from e

    yaml_files = [entry for entry in data_dir.iterdir() if entry.name.endswith(".yaml")]
    if not yaml_files:
        raise DataDefinitionError(
            "No YAML files found in discoanalytica.data_definition.data_definitions."
        )

    print("Available data definitions:")
    for i, entry in enumerate(yaml_files, start=1):
        print(f"  {i}. {entry.name}")

    while True:
        user_input = input("Pick a data source by number: ")
        try:
            choice = int(user_input)
            if 1 <= choice <= len(yaml_files):
                selected = yaml_files[choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(yaml_files)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    with as_file(selected) as file_path:
        data_definition = DataDefinition.from_yaml_file(file_path)

    return data_definition
