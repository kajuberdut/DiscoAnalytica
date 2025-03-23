from discoanalytica.data_definition import DataDefinition, register_definition_handler
from discoanalytica.database import Database


@register_definition_handler("metadata.data_definition")
def insert_into_db(data_definition: DataDefinition, step: dict) -> int:
    """
    Insert this DataDefinition instance into the data_definitions table using the provided DuckDB connection
    and return the generated data_definition_id.

    Returns:
        int: The auto-generated data_definition_id from the insert.
    """
    query = """
    INSERT INTO data_definitions (
          name
        , license
        , attribution
    )
    VALUES (?, ?, ?, )
    RETURNING data_definition_id
    """
    params = (
        data_definition["name"],
        data_definition["license"],
        data_definition["attribution"],
    )
    with Database() as db:
        cursor = db.execute(query, params)
        data_definition_id = cursor.fetchone()[0]
        data_definition["data_definition_id"] = data_definition_id
