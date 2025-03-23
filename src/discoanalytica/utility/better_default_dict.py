from collections import defaultdict
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class BetterDefaultDict(defaultdict, Generic[K, V]):
    """
    A defaultdict subclass with a cleaner __repr__.

    When printed, it shows the default_factory (by its name, if possible)
    and the contained dictionary data.
    """

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        # If no default_factory is provided, simply show the dict representation.
        if self.default_factory is None:
            return f"{cls_name}({dict(self)!r})"

        # Attempt to show a user-friendly name for the default_factory.
        if hasattr(self.default_factory, "__name__"):
            factory_name = self.default_factory.__name__
        else:
            factory_name = repr(self.default_factory)

        return f"{cls_name}(default_factory={factory_name}, data={dict(self)!r})"


# Example usage:
if __name__ == "__main__":
    # Create a BetterDefaultDict with int as the default_factory.
    d = BetterDefaultDict(int)
    d["apple"] += 1
    d["banana"] += 2
    print(
        d
    )  # Output: BetterDefaultDict(default_factory=int, data={'apple': 1, 'banana': 2})
