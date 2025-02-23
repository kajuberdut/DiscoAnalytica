import duckdb

from discoanalytica.get_paths import DATA_PATH
from discoanalytica.models.data_source import DataSource

DB_PATH = DATA_PATH / "discoanalytica.duckdb"

conn = duckdb.connect(DB_PATH)

def import_csv(data_source: DataSource) -> None:
    load_csv_sql = f"""
    CREATE TABLE {data_source.name} AS
    SELECT *
    FROM read_csv_auto('{data_source.file_path}', header=True)
    ;
    """
    conn.execute(load_csv_sql)
