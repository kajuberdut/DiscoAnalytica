import uuid
from datetime import datetime

from discoanalytica.errors import UnknownOperation
from discoanalytica.models.data_definition import DataDefinition
from discoanalytica.models.database import Database


def record_table_info(conn, table_name: str, table_type_str: str) -> int:
    """
    Inserts a row into table_info for the given table.

    Args:
        conn: A DuckDB connection.
        table_name: The name of the table that was created.
        table_type_str: The type of the table as a string (e.g., "Entity Table").

    Returns:
        The table_info_id generated for the inserted row.

    Raises:
        Exception: If the table_type is not found.
    """
    # Get the type_id from table_type based on the table type string
    query = "SELECT type_id FROM table_type WHERE name = ?"
    cur = conn.execute(query, (table_type_str,))
    row = cur.fetchone()
    if row is None:
        raise Exception(f"Table type '{table_type_str}' not found in table_type table")
    type_id = row[0]

    # Insert the new table info and return the generated table_info_id
    insert_sql = "INSERT INTO table_info (table_name, type_id) VALUES (?, ?) RETURNING table_info_id"
    cur = conn.execute(insert_sql, (table_name, type_id))
    table_info_id = cur.fetchone()[0]
    return table_info_id


def record_data_log(
    conn,
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
        conn: A DuckDB connection.
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


def process_data_pipeline(data_definition: DataDefinition):
    """
    Processes a sequence of SQL operations described in a JSON-like list.

    For each operation:
      - Executes "create_sequence" SQL statements.
      - Executes "create_table" SQL statements and then logs the table in table_info.
      - Executes "insert_data" SQL statements and logs each insert into data_log.

    A UUID is generated at the start to be used as the data_load_session_id for all logs.

    Args:
        data_definition: An discoanalytica data_definition
    """
    with Database() as conn:
        data_definition.insert_into_db(conn)

        # Generate a session UUID for the entire pipeline run.
        session_id = str(uuid.uuid4())

        # Process each step in the sequence.
        for step in data_definition.data_pipeline:
            step_type = step.get("type")

            if step_type == "create_sequence":
                # Execute the sequence creation SQL.
                conn.execute(step["sql"])

            elif step_type == "create_table":
                # Execute the create table SQL.
                conn.execute(step["sql"])
                table_name = step["name"]
                table_type_str = step.get("table_type")
                if table_type_str:
                    # Record the table creation in table_info.
                    record_table_info(conn, table_name, table_type_str)

            elif step_type == "insert_data":
                # For an insert operation, first obtain the corresponding table_info_id.
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
                record_data_log(
                    conn,
                    session_id,
                    data_definition.data_definition_id,
                    table_info_id,
                    load_start_time,
                    load_end_time,
                    rows_affected,
                )

            else:
                raise UnknownOperation(f"Got unknown {step_type=}")
