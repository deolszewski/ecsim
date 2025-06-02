import random

from constants import Parameters
from objects import Action, Creature, Plant, Population


class Environment:
    def __init__(self) -> None:
        self.population: Population = Population(
            general=self._populate(
                n_creatures=Parameters.STARTING_CREATURES,
                n_plants=Parameters.STARTING_PLANTS,
            ),
        )

    @staticmethod
    def _populate(n_creatures: int, n_plants: int) -> list:
        return (
            [
                Creature(
                    x=random.randint(0, 100),
                    y=random.randint(0, 100),
                    diet="carnivore",
                    MAX_ATP=200,
                )
                for _ in range(n_creatures)
            ]
            + [
                Creature(
                    x=random.randint(0, 100),
                    y=random.randint(0, 100),
                    diet="herbivore",
                    MAX_ATP=80,
                )
                for _ in range(n_creatures)
            ]
            + [
                Plant(x=random.randint(0, 100), y=random.randint(0, 100))
                for _ in range(n_plants)
            ]
        )  # TODO Change the population implementation
        # + random.randint -> random.unfirom || numpy


class Simulation:
    def __init__(self) -> None:
        self.environment = Environment()

    def _execute_action(  # TODO Change the Action implementation
        self,
        obj: Creature,
        action: Action,
    ) -> None:
        match action.type:
            case "die":
                self.environment.population.general.remove(obj)
            case "reproduce":  # Also counts for Plant crops
                self.environment.population.general.append(action.payload)
            case "wander" | "goto" | "escape":
                x_movement, y_movement = action.movement
                if 0 < obj.x + x_movement < Parameters.ENV_WIDTH:
                    obj.x += x_movement
                if 0 < obj.y + y_movement < Parameters.ENV_HEIGHT:
                    obj.y += y_movement
            case "eat":
                calories_consumed = obj.consume(obj=action.payload)
                is_eaten = action.payload.consumed(
                    calories_consumed=calories_consumed,
                )  # TODO Events?
                if is_eaten:
                    self.environment.population.general.remove(action.payload)
            case "dead":
                pass

    def update_environment(self) -> None:
        for obj in self.environment.population.general:  # Temporary solution
            action = obj.update(
                population=self.environment.population,
            )
            self._execute_action(obj=obj, action=action)
