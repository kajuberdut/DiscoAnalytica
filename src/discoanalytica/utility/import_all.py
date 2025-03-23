import importlib
import importlib.resources


def import_all_modules(package_name: str) -> None:
    """
    Import all modules in the specified package using importlib.resources.files.

    This approach is modern and leverages the newer importlib.resources API.
    """
    package = importlib.import_module(package_name)
    package_files = importlib.resources.files(package)

    # Iterate over all files in the package
    for entry in package_files.iterdir():
        # Check if the entry is a .py file (ignoring __init__.py)
        if entry.suffix == ".py" and entry.name != "__init__.py":
            module_name = entry.stem
            importlib.import_module(f"{package_name}.{module_name}")


# Example usage:
if __name__ == "__main__":
    # Automatically import all modules in the 'myproject.handlers' package
    import_all_modules("myproject.handlers")
    # Now all handler decorators should have executed.
