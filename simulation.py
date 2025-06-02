import numpy as np

from constants import Parameters
from objects import Creature, Plant, Population


class Environment:
    def __init__(self) -> None:
        self.population = Population(
            general=self._populate(
                n_creatures=Parameters.STARTING_CREATURES,
                n_plants=Parameters.STARTING_PLANTS,
            ),
        )

    @staticmethod
    def _populate(n_creatures: int, n_plants: int) -> list:
        l = (
            [
                Creature(
                    x=np.random.randint(0, 100),
                    y=np.random.randint(0, 100),
                    diet="carnivore",
                )
                for _ in range(n_creatures)
            ]
            + [
                Creature(
                    x=np.random.randint(0, 100),
                    y=np.random.randint(0, 100),
                    diet="herbivore",
                )
                for _ in range(n_creatures)
            ]
            + [
                Plant(x=np.random.randint(0, 100), y=np.random.randint(0, 100))
                for _ in range(n_plants)
            ]
        )
        return l


class Simulation:
    def __init__(self) -> None:
        self.environment = Environment()

    def update_environment(self) -> None:
        for i, object in enumerate(self.environment.population.plants):
            rep = object.yield_crops()
            if rep:
                self.environment.population.general.append(rep)
        for i, object in enumerate(self.environment.population.creatures):
            action = object.update(
                population=self.environment.population,
            )
            x_movement, y_movement = action.movement
            match action.type:
                case "die":
                    self.environment.population.general.remove(object)
                case "reproduce":
                    self.environment.population.general.append(action.payload)
                case "wander" | "goto":
                    if object.x + x_movement < Parameters.ENV_WIDTH:
                        object.x += x_movement
                    if object.y + y_movement < Parameters.ENV_HEIGHT:
                        object.y += y_movement
                case "eat":
                    c = action.payload.consumed()
                    if c:
                        self.environment.population.general.remove(action.payload)
                    print(f"{i} - Eaten, ATP = {object.ATP}")

            # print(f'Movement From: {i} - x: {x_movement}, y: {y_movement}')
