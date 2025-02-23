import csv
from pathlib import Path

def validate_csv(file_path: Path):
    """Ensure the input file is a CSV."""
    if not file_path.is_file():
        raise ValueError(f"Input file '{file_path}' does not exist.")
    if file_path.suffix.lower() != ".csv":
        raise ValueError("Input file must be a .csv")

def validate_output_dir(output_dir: Path):
    """Ensure the output directory exists."""
    if not output_dir.exists():
        raise ValueError(f"Output directory '{output_dir}' does not exist.")

def create_preview_csv(csv_path: Path, output_dir: Path):
    """Create a preview CSV with header + first 5 rows."""
    validate_csv(csv_path)
    validate_output_dir(output_dir)
    preview_file = output_dir / f"preview_{csv_path.stem}.csv"
    with csv_path.open("r", newline="") as f_in, preview_file.open("w", newline="") as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        for i, row in enumerate(reader):
            writer.writerow(row)
            if i == 5:  # Write header + first 5 rows
                break
    return preview_file
