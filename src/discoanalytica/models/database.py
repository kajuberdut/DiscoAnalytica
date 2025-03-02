import os
from importlib.resources import path as resource_path
from pathlib import Path

import duckdb

from discoanalytica.paths import DATA_PATH

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
        SELECT COUNT(*) = 6
        FROM INFORMATION_SCHEMA.TABLES
        WHERE table_name IN (
            'data_definitions'
          , 'data_file_type'
          , 'data_log'
          , 'data_provider'
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
