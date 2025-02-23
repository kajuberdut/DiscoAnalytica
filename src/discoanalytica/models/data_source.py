import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Type, TypeVar, Union

from discoanalytica.file_hash import check_file_hash


class Provider(Enum):
    KAGGLE = 1


class SourceType(Enum):
    CSV = 1
    PARQUET = 2
    JSON = 3


T = TypeVar("T", bound=Enum)


def coerce_enum(enum_type: Type[T], value: str | T) -> T:
    if isinstance(value, enum_type):
        return value
    try:
        return enum_type[value]
    except ValueError as e:
        raise ValueError(f"Invalid value '{value}' for {enum_type.__name__}") from e


@dataclass
class DataSource:
    name: str
    external_id: Union[str, int]
    provider: Provider
    url: str
    source_type: SourceType
    license: str
    attribution: str
    hash: str
    filename: str
    _file_path: Path = field(default=None, repr=False)

    def __post_init__(self):
        self.provider = coerce_enum(Provider, self.provider.upper())
        self.source_type = coerce_enum(SourceType, self.source_type.upper())

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
            if not fp.is_file():
                if self.filename:
                    fp = fp / self.filename
                if not fp.is_file():
                    raise ValueError("File path is not a valid path to a file.")
            self._file_path = fp

    @property
    def external_id_as_int(self) -> int:
        """
        Retrieve the id as an integer. If the id is not directly convertible,
        a ValueError will be raised.
        """
        try:
            return int(self.external_id)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot convert id {self.external_id!r} to int.") from e

    @property
    def valid_hash(self) -> bool:
        return check_file_hash(self.file_path, self.hash)

    @classmethod
    def from_json_file(cls, json_file: Path) -> "DataSource":
        """
        Load a DataSource instance from a JSON file.

        Args:
            json_file (Path): The path to the JSON file.

        Returns:
            DataSource: The loaded DataSource instance.
        """
        data = json.loads(json_file.read_text(encoding="utf-8"))
        return cls(**data, **{"name": json_file.stem})
