import argparse
from pathlib import Path

from . import manage_data


def main():
    parser = argparse.ArgumentParser(
        prog="discoanalytica", description="DiscoAnalytica CLI tool"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand 'add'
    data_parser = subparsers.add_parser(
        "add", help="Compress a CSV file using LZMA and generate an attribution.json"
    )
    data_parser.add_argument("input_csv", type=Path, help="Path to the input CSV file")
    data_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path().cwd,
        help="Output directory (default: current directory)",
    )
    data_parser.set_defaults(func=manage_data.main)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
