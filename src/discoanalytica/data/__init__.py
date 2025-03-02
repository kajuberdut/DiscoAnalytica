from importlib.resources import as_file, files
from typing import Callable, Dict

from discoanalytica.data.file_types.csv import import_csv
from discoanalytica.data.pipeline import process_data_pipeline
from discoanalytica.data.providers.kaggle import kaggle_download
from discoanalytica.errors import DataDefinitionError
from discoanalytica.models.data_definition import (
    DataDefinition,
    DataFileType,
    DataProvider,
)

PROVIDER_HANDLERS: Dict[DataProvider, Callable[[DataDefinition], None]] = {
    DataProvider.KAGGLE: kaggle_download,
}

FILE_TYPE_HANDLERS: Dict[DataProvider, Callable[[DataDefinition], None]] = {
    DataFileType.CSV: import_csv,
}


def process_provider(data_definition: DataDefinition):
    handler = PROVIDER_HANDLERS.get(data_definition.provider)
    if handler:
        handler(data_definition)
    else:
        raise ValueError(f"No handler for provider: {data_definition.provider}")


def process_file(data_definition: DataDefinition):
    handler = FILE_TYPE_HANDLERS.get(data_definition.file_type)
    if handler:
        handler(data_definition)
    else:
        raise ValueError(f"No handler for file type: {data_definition.file_type}")


def pick_data_definition() -> DataDefinition:
    """
    Presents a numbered list of .json files from the
    discoanalytica.data_definitions package, allows the user to pick one,
    and returns a DataDefinition object from the chosen file.

    Raises:
        DataDefinitionError: If the data_definitions package cannot be accessed
                         or if no JSON files are found.
    """
    try:
        data_dir = files("discoanalytica.data_definitions")
    except Exception as e:
        raise DataDefinitionError(
            f"Error accessing discoanalytica.data_definitions: {e}"
        ) from e

    json_files = [entry for entry in data_dir.iterdir() if entry.name.endswith(".json")]
    if not json_files:
        raise DataDefinitionError(
            "No JSON files found in discoanalytica.data_definitions."
        )

    print("Available data definitions:")
    for i, entry in enumerate(json_files, start=1):
        print(f"  {i}. {entry.name}")

    while True:
        user_input = input("Pick a data source by number: ")
        try:
            choice = int(user_input)
            if 1 <= choice <= len(json_files):
                selected = json_files[choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(json_files)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    with as_file(selected) as file_path:
        data_definition = DataDefinition.from_json_file(file_path)

    return data_definition


def process_data_definition():
    data_definition = pick_data_definition()
    process_provider(data_definition)
    process_file(data_definition)
    process_data_pipeline(data_definition)
