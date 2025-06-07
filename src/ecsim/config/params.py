from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Parameters:
    STARTING_PLANTS: Final[int] = 50
    STARTING_CREATURES: Final[int] = 3
    ENV_WIDTH: Final[int] = 100
    ENV_HEIGHT: Final[int] = 100
