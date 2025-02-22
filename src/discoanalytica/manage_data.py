import argparse
import json
import lzma
import shutil
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

def compress_csv(input_csv: Path, output_dir: Path):
    """Compress the CSV file using lzma, generate an attribution JSON, and create a preview CSV."""
    # Validate input
    validate_csv(input_csv)
    validate_output_dir(output_dir)
    
    # Create a sub-directory named after the CSV file (without suffix)
    sub_dir = output_dir / input_csv.stem
    sub_dir.mkdir(parents=True, exist_ok=True)
    
    # Compress CSV file
    compressed_file = sub_dir / f"{input_csv.name}.xz"
    with input_csv.open("rb") as f_in, lzma.open(compressed_file, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    
    # Create a preview CSV with header + first 5 rows
    preview_file = sub_dir / f"preview_{input_csv.stem}.csv"
    with input_csv.open("r", newline="") as f_in, preview_file.open("w", newline="") as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        for i, row in enumerate(reader):
            writer.writerow(row)
            if i == 5:  # Write header + first 5 rows
                break
    
    # Create an attribution.json file
    attribution_data = {
        "dataset": {
            "name": input_csv.stem,
            "author": "",
            "source": "",
            "url": "",
            "license": "",
            "attribution": ""
        }
    }
    attribution_file = sub_dir / "attribution.json"
    with attribution_file.open("w", encoding="utf-8") as f:
        json.dump(attribution_data, f, indent=4)
    
    print(f"CSV compressed and stored at: {compressed_file}")
    print(f"Preview CSV created at: {preview_file}")
    print(f"Attribution JSON created at: {attribution_file}")

def main(args=None):
    if args is None:
        parser = argparse.ArgumentParser(description="Compress a CSV file using LZMA and generate an attribution.json.")
        parser.add_argument("input_csv", type=Path, help="Path to the input CSV file.")
        parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent, help="Output directory (default: script's parent directory)")
        args = parser.parse_args()
    
    compress_csv(args.input_csv, args.output_dir)

if __name__ == "__main__":
    main()
