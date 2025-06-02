from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Parameters:
    STARTING_PLANTS: Final[int] = 50
    STARTING_CREATURES: Final[int] = 50
    ENV_WIDTH = 100
    ENV_HEIGHT = 100
