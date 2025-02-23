from importlib.resources import as_file, files

import kagglehub

from discoanalytica.errors import BadHashError, DataSourceError
from discoanalytica.models.data_source import DataSource


def kaggle_download(data_source: DataSource) -> DataSource:
    result_path = kagglehub.dataset_download(data_source.external_id)
    data_source.file_path = result_path

    if not data_source.valid_hash:
        raise BadHashError("The file hash did not match.")

    return data_source


def pick_data_source() -> DataSource:
    """
    Presents a numbered list of .json files from the
    discoanalytica.data_sources package, allows the user to pick one,
    and returns a DataSource object from the chosen file.

    Raises:
        DataSourceError: If the data_sources package cannot be accessed
                         or if no JSON files are found.
    """
    try:
        data_dir = files("discoanalytica.data_sources")
    except Exception as e:
        raise DataSourceError(
            f"Error accessing discoanalytica.data_sources: {e}"
        ) from e

    json_files = [entry for entry in data_dir.iterdir() if entry.name.endswith(".json")]
    if not json_files:
        raise DataSourceError("No JSON files found in discoanalytica.data_sources.")

    print("Available data sources:")
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
        data_source = DataSource.from_json_file(file_path)

    return data_source

def load_data(data_source) -> DataSource:

if __name__ == "__main__":
    try:
        data_source = pick_data_source()
        print(f"Data source: {data_source}")
    except DataSourceError as e:
        print(f"Error: {e}")

    kaggle_download(data_source)
