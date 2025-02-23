from importlib.resources import path

import duckdb

with path("discoanalytica.sql", "music-dataset-1950-to-2019.sql") as sql_path:
    print(sql_path)


sql_parse = PARSE_SQL_PATH.read_text("utf-8")

conn = duckdb.connect(DB_PATH)


conn.execute(sql_parse)
