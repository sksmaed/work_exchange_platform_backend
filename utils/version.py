from typing import NamedTuple


class Version(NamedTuple):
    """Version object with major, minor, patch, and alpha version."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        """Return the version string."""
        return f"v{self.major}.{self.minor}.{self.patch}"


CURRENT_VERSION = Version(
    major=2,
    minor=0,
    patch=1,
    alpha=5,
)


def get_version() -> str:
    """Return the current version string."""
    return str(CURRENT_VERSION)
