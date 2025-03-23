from discoanalytica.data_definition import DataDefinition, register_definition_handler
from discoanalytica.errors import BadHashError
from discoanalytica.utility.file_hash import check_file_hash


@register_definition_handler("validate.hash")
def valid_hash(data_definition: DataDefinition, step: dict) -> None:
    fp = data_definition.file_path
    for file_name, target_hash in step["hashes"].items():
        if check_file_hash((fp / file_name), target_hash) is False:
            raise BadHashError(f"{fp} does not match {target_hash}")
