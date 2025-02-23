from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict

# Define the Source Enum
class Source(Enum):
    API = "api"
    CSV = "csv"
    DATABASE = "database"

# Define your processing functions
def handle_api(item):
    print(f"Handling API source for {item}")

def handle_csv(item):
    print(f"Handling CSV source for {item}")

def handle_database(item):
    print(f"Handling Database source for {item}")

# Define a mapping of Enum values to functions
SOURCE_HANDLERS: Dict[Source, Callable[['DataItem'], None]] = {
    Source.API: handle_api,
    Source.CSV: handle_csv,
    Source.DATABASE: handle_database,
}

# Define the dataclass
@dataclass
class DataItem:
    source: Source
    data: str  # Example additional field

    def process(self):
        """Calls the correct function based on self.source"""
        handler = SOURCE_HANDLERS.get(self.source)
        if handler:
            handler(self)
        else:
            raise ValueError(f"No handler for source: {self.source}")

# Example Usage
item1 = DataItem(source=Source.API, data="example")
item2 = DataItem(source=Source.CSV, data="another example")

item1.process()  # Calls handle_api
item2.process()  # Calls handle_csv
