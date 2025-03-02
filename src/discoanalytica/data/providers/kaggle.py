import kagglehub

from discoanalytica.errors import BadHashError
from discoanalytica.models.data_definition import DataDefinition


def kaggle_download(data_definition: DataDefinition) -> DataDefinition:
    result_path = kagglehub.dataset_download(data_definition.external_id)
    data_definition.file_path = result_path

    if not data_definition.valid_hash:
        raise BadHashError("The file hash did not match.")

    return data_definition
