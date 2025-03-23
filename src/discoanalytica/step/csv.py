from discoanalytica.data_definition import DataDefinition, register_definition_handler
from discoanalytica.database import Database
from discoanalytica.utility.file_locator import locate_unique_file_by_extension


@register_definition_handler("csv.import")
def import_csv(data_definition: DataDefinition, step: dict) -> None:
    raw_table_name = data_definition["name"].replace("-", "_")
    file_handle = locate_unique_file_by_extension(data_definition.file_path, ".csv")
    load_csv_sql = f"""
    CREATE TABLE {raw_table_name} AS
    SELECT *
    FROM read_csv_auto('{file_handle}', header=True)
    ;
    """
    with Database() as db:
        db.execute(load_csv_sql)
    data_definition["raw_table_name"] = raw_table_name
