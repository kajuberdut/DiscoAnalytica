import csv
from pathlib import Path

from discoanalytica.models.data_definition import DataDefinition
from discoanalytica.models.database import Database


def create_preview_csv(data_definition: DataDefinition, output_dir: Path):
    """Create a preview CSV with header + first 5 rows."""
    preview_file = output_dir / f"preview_{data_definition.file_path.stem}.csv"
    with (
        data_definition.file_path.open("r", newline="") as f_in,
        preview_file.open("w", newline="") as f_out,
    ):
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        for i, row in enumerate(reader):
            writer.writerow(row)
            if i == 5:  # Write header + first 5 rows
                break
    return preview_file


def import_csv(data_definition: DataDefinition) -> None:
    raw_table_name = data_definition.name.replace("-", "_")
    load_csv_sql = f"""
    CREATE TABLE {raw_table_name} AS
    SELECT *
    FROM read_csv_auto('{data_definition.file_path}', header=True)
    ;
    """
    with Database() as db:
        db.execute(load_csv_sql)
