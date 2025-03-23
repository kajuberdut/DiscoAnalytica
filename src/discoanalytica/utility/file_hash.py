import argparse
import hashlib
from pathlib import Path


def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Compute the hash of the file at file_path using the specified hash algorithm.

    Args:
        file_path (Path): The path to the file.
        algorithm (str): The hash algorithm to use (default: 'sha256').

    Returns:
        str: The hexadecimal digest of the file's hash.
    """
    hash_func = hashlib.new(algorithm)
    file_bytes = file_path.read_bytes()
    hash_func.update(file_bytes)
    return hash_func.hexdigest()


def check_file_hash(
    file_path: Path, expected_hash: str, algorithm: str = "sha256"
) -> bool:
    """
    Check if the hash of the file at file_path matches the expected hash.

    Args:
        file_path (Path): The path to the file.
        expected_hash (str): The expected hash value (hexadecimal string).
        algorithm (str): The hash algorithm to use (default: 'sha256').

    Returns:
        bool: True if the computed hash matches expected_hash, False otherwise.
    """
    computed_hash = compute_file_hash(file_path, algorithm)
    return computed_hash == expected_hash


def main():
    parser = argparse.ArgumentParser(
        description="Compute or verify a file hash using built-in Python libraries."
    )
    parser.add_argument("file", type=Path, help="Path to the file to hash")
    parser.add_argument(
        "--algorithm", default="sha256", help="Hash algorithm to use (default: sha256)"
    )
    parser.add_argument(
        "--expected",
        help="Expected hash value. If provided, the file's hash is compared to this value.",
    )
    args = parser.parse_args()

    try:
        if args.expected:
            computed_hash = compute_file_hash(args.file, args.algorithm)
            print(f"Computed hash: {computed_hash}")
            if check_file_hash(args.file, args.expected, args.algorithm):
                print("File hash matches the expected value.")
                exit(0)
            else:
                print("File hash does NOT match the expected value.")
                exit(1)
        else:
            computed_hash = compute_file_hash(args.file, args.algorithm)
            print(f"Computed hash: {computed_hash}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
