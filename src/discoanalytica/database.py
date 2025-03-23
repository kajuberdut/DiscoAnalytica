import os
import re
from datetime import datetime
from importlib.resources import path as resource_path
from pathlib import Path

import duckdb

from discoanalytica.data_definition import DataDefinition, register_definition_handler
from discoanalytica.paths import DATA_PATH


def is_valid_sql_name(name) -> bool:
    return bool(re.fullmatch(r"[a-z_]+", name))


# Determine the database path from the environment variable.
disco_db_path_env = os.environ.get("DISCO_DB_PATH")
if disco_db_path_env:
    candidate = Path(disco_db_path_env)
    if candidate.is_absolute():
        DB_PATH = candidate
    else:
        DB_PATH = DATA_PATH / candidate
else:
    DB_PATH = DATA_PATH / "discoanalytica.duckdb"


class Database:
    """
    A wrapper for a DuckDB connection that lazily creates the connection on first use.
    It ensures that the base tables exist and provides a method to clear (close and delete)
    the database file.
    """

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._conn = None

    def _connect(self) -> duckdb.DuckDBPyConnection:
        """
        Lazily create the connection. On first connection, ensure that the base
        tables exist.
        """
        if self._conn is None:
            self._conn = duckdb.connect(str(self.db_path))
            self._confirm_base_tables_exist()
        return self._conn

    def _confirm_base_tables_exist(self) -> None:
        """
        Checks if the required base tables exist. If not, it loads and executes the
        base table creation SQL from the 'base_tables.sql' file.
        """
        BASE_CHECK = """
        SELECT COUNT(*) = 4
        FROM INFORMATION_SCHEMA.TABLES
        WHERE table_name IN (
            'data_definitions'
          , 'data_log'
          , 'table_info'
          , 'table_type'
        );
        """
        self._conn.execute(BASE_CHECK)
        result = self._conn.fetchone()
        if not result[0]:
            print("Base tables not found, creating.")
            with resource_path("discoanalytica.sql", "base_tables.sql") as sql_path:
                base_sql = sql_path.read_text("utf-8")
                self._conn.execute(base_sql)

    def clear_db(self) -> None:
        """
        Closes the connection (if open) and deletes the database file.
        """
        self.close()
        if self.db_path.exists():
            self.db_path.unlink()

    def close(self) -> None:
        """
        Closes the DuckDB connection if it is open.
        """
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __getattr__(self, name: str):
        """
        Delegate attribute access to the underlying connection object.
        This allows the Database instance to mimic a DuckDB connection.
        """
        conn = self._connect()
        return getattr(conn, name)

    def __enter__(self) -> duckdb.DuckDBPyConnection:
        """
        Support for context manager 'with' statement.
        """
        return self._connect()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Ensures that the connection is closed when exiting a context.
        """
        self.close()


def clear_db():
    confirmation = input(
        "WARNING: This will permanently delete all data in the database.\n"
        "Type 'DELETE' to confirm: "
    )
    if confirmation == "DELETE":
        Database().clear_db()
        print("Database has been cleared.")
    else:
        print("Confirmation not received. Aborting deletion.")


def record_table_info(table_name: str, table_type_str: str) -> int:
    """
    Inserts a row into table_info for the given table.

    Args:
        table_name: The name of the table that was created.
        table_type_str: The type of the table as a string (e.g., "Entity Table").

    Returns:
        The table_info_id generated for the inserted row.

    Raises:
        Exception: If the table_type is not found.
    """
    # Get the type_id from table_type based on the table type string
    query = "SELECT type_id FROM table_type WHERE name = ?"
    with Database() as conn:
        cur = conn.execute(query, (table_type_str,))
        row = cur.fetchone()
    if row is None:
        raise Exception(f"Table type '{table_type_str}' not found in table_type table")
    type_id = row[0]

    # Insert the new table info and return the generated table_info_id
    insert_sql = "INSERT INTO table_info (table_name, type_id) VALUES (?, ?) RETURNING table_info_id"
    with Database() as conn:
        cur = conn.execute(insert_sql, (table_name, type_id))
        table_info_id = cur.fetchone()[0]
    return table_info_id


def insert_data_log(
    session_id: str,
    data_definition_id: int,
    table_info_id: int,
    load_start_time: int,
    load_end_time: int,
    rows_affected: int,
):
    """
    Inserts a row into the data_log table to log an insert operation.

    Args:
        session_id: The UUID for the data load session.
        data_definition_id: The data definition id passed to the pipeline.
        table_info_id: The table_info_id corresponding to the target table.
        load_start_time: The start time (in milliseconds) of the insert operation.
        load_end_time: The end time (in milliseconds) of the insert operation.
        rows_affected: The number of rows affected by the insert.
    """
    insert_sql = """
      INSERT INTO data_log (
          data_load_session_id, table_info_id, data_definition_id, 
          load_start_time, load_end_time, rows_affected
      )
      VALUES (?, ?, ?, ?, ?, ?)
    """
    with Database() as conn:
        conn.execute(
            insert_sql,
            (
                session_id,
                table_info_id,
                data_definition_id,
                load_start_time,
                load_end_time,
                rows_affected,
            ),
        )


def create_sequence(sequence_name: str, start: int = 1) -> None:
    if not is_valid_sql_name(sequence_name):
        raise RuntimeError(
            "sequence_name must contain only lowercase letters and underscore."
        )

    with Database() as conn:
        conn.execute(
            f"CREATE SEQUENCE IF NOT EXISTS {sequence_name} START {int(start)};"
        )

@register_definition_handler("sql.sequence")
def create_sequence_step(data_definition: DataDefinition, step: dict) -> None:
    create_sequence(step["name"])

@register_definition_handler("sql.table")
def create_table_step(data_definition: DataDefinition, step: dict) -> None:
    with Database() as conn:

        conn.execute(step["sql"])
        table_name = step["name"]
        table_type_str = step.get("table_type")
        if table_type_str:
            # Record the table creation in table_info.
            record_table_info(table_name, table_type_str)

@register_definition_handler("sql.insert")
def insert_data(data_definition: DataDefinition, step: dict) -> None:
    with Database() as conn:
        table_name = step.get("table")
        # Retrieve table_info_id for the target table.
        cur = conn.execute(
            "SELECT table_info_id FROM table_info WHERE table_name = ?",
            (table_name,),
        )
        row = cur.fetchone()
        if row is None:
            raise Exception(
                f"Table info for table '{table_name}' not found. Ensure the table was created and logged."
            )
        table_info_id = row[0]

        # Record the start time.
        load_start_time = datetime.now()
        # Execute the insert statement.
        result = conn.execute(step["sql"])
        # Attempt to get the number of rows affected.
        try:
            rows_affected = result.rowcount
        except AttributeError:
            rows_affected = 0
        # Record the end time.
        load_end_time = datetime.now()
        # Log the insert operation.
        insert_data_log(
            data_definition["session_id"],
            data_definition["data_definition_id"],
            table_info_id,
            load_start_time,
            load_end_time,
            rows_affected,
        )
