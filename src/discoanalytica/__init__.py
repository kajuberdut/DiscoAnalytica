import argparse

from discoanalytica.data import pick_data_definition
from discoanalytica.models.database import clear_db


def main():
    parser = argparse.ArgumentParser(description="DiscoAnalytica CLI")

    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    loader_parser = subparsers.add_parser("loader", help="Run the data loader")

    parser.add_argument("--clear-db", action="store_true", help="Clear the database")

    args = parser.parse_args()

    if args.clear_db:
        clear_db()

    if args.command == "loader":
        data_definition = pick_data_definition()
        print("Data definition loaded successfully.")
    else:
        print("Hello, this is the main entrypoint of discoanalytica")
        print("Currently there is no functionality here.")


if __name__ == "__main__":
    main()
