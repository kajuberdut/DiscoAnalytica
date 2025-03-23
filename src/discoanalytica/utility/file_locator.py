from pathlib import Path

from discoanalytica.errors import FileValidationError


def locate_unique_file_by_extension(path: Path, extension: str) -> Path:
    """
    Validate that the provided path is either:
      - A file with the given extension, or
      - A directory containing exactly one file with that extension.

    If validation passes, return the matching file's Path.
    Otherwise, raise a FileValidationError.

    Args:
        path (Path): The file or directory to validate.
        extension (str): The file extension (e.g. '.txt'). If it doesn't start with a dot,
                         one will be prepended.

    Returns:
        Path: The validated file's path.

    Raises:
        FileValidationError: If the path doesn't meet the validation criteria.
    """
    # Ensure the extension starts with a dot.
    if not extension.startswith("."):
        extension = "." + extension

    if path.is_file():
        if path.suffix == extension:
            return path
        else:
            raise FileValidationError(
                f"The file '{path}' does not have the required extension '{extension}'."
            )

    elif path.is_dir():
        # Find all files in the directory that have the desired extension.
        matching_files = list(path.glob(f"*{extension}"))
        if len(matching_files) == 1:
            return matching_files[0]
        elif not matching_files:
            raise FileValidationError(
                f"No files with extension '{extension}' were found in the directory '{path}'."
            )
        else:
            raise FileValidationError(
                f"Multiple files with extension '{extension}' were found in the directory '{path}': {matching_files}"
            )

    else:
        raise FileValidationError(
            f"The path '{path}' is neither a valid file nor a directory."
        )
