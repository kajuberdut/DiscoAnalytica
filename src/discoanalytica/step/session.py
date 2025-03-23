import uuid

from discoanalytica.data_definition import DataDefinition, register_definition_handler


@register_definition_handler("session.get_id")
def get_session_id(data_definition: DataDefinition, step: dict) -> None:
    # Generate a session UUID for the entire pipeline run.
    data_definition["session_id"] = str(uuid.uuid4())
