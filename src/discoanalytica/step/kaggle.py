import kagglehub

from discoanalytica.data_definition import DataDefinition, register_definition_handler

@register_definition_handler("fetch.kaggle")
def kaggle_download(data_definition: DataDefinition, step: dict) -> None:
    result_path = kagglehub.dataset_download(step["id"])
    data_definition.file_path = result_path
