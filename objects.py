from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np


@dataclass  # TODO Move to simulation.py?
class Population:
    general: list

    @property
    def creatures(self) -> list:
        return [obj for obj in self.general if isinstance(obj, Creature)]

    @property
    def plants(self) -> list:
        return [obj for obj in self.general if isinstance(obj, Plant)]

    @property
    def consumables(self) -> list:
        return [obj for obj in self.general if isinstance(obj, Consumable)]

    @property
    def carnivores(self) -> list:
        return [obj for obj in self.creatures if obj.DIET == "carnivore"]

    @property
    def herbivores(self) -> list:
        return [obj for obj in self.creatures if obj.DIET == "herbivore"]


@dataclass
class Object:
    x: float
    y: float


@dataclass
class Action:
    movement: tuple[float, float] = (0.0, 0.0)
    type: str = ""
    payload: Creature | Plant | Consumable | None = None


# TODO: class Corpse(Object):


@dataclass
class Consumable(Object):
    parent: Plant
    caloric_value: float

    def consumed(self, calories_consumed: float) -> bool:
        self.is_alive = False
        self.caloric_value -= calories_consumed
        return self.caloric_value <= 0

    def update(self, population: Population) -> Action:
        return Action()


class Plant(Object):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        # Genome / Specie-dependent in the future
        self.MAX_YIELD: int = random.randint(3, 15)
        self.CHILD_CALORIC_VALUE: float = 25

        # Dynamic attributes
        self.current_yield: int = 0

        # State-defining attributes
        self.parent: list = []

    def yield_crops(
        self,
    ) -> Consumable | None:  # Error if i put Plant class above Consumable
        if random.randint(1, 1000) == 1 and self.current_yield < self.MAX_YIELD:
            self.current_yield += 1
            return Consumable(
                x=random.randint(-1, 1) + self.x,
                y=random.randint(-1, 1) + self.y,
                parent=self,
                caloric_value=self.CHILD_CALORIC_VALUE,
            )
        return None

    def update(self, population: Population) -> Action:
        crops = self.yield_crops()
        if crops:
            return Action(type="reproduce", payload=crops)
        return Action()


@dataclass
class HormonalSystem:
    LEPTIN_SENSITIVITY: float = 0.05
    GHERLIN_BASE: float = 0.3
    METABOLISM: float = 0.1

    leptin: float = 1.0  # Satiation hormone
    gherlin: float = 0.0  # Hunger hormone

    def update(self, current_atp: float, max_atp: float) -> float:
        self.leptin = self.LEPTIN_SENSITIVITY * current_atp
        self.gherlin = self.GHERLIN_BASE + (1 - current_atp / max_atp)

        eating_urge = 1 / (
            1 + np.exp(-2 * (self.gherlin - self.leptin))
        )  # TODO Exponentials
        return min(max(eating_urge, 0), 1)  # 0-1


class Creature(Object):
    def __init__(self, x: float, y: float, diet: str, MAX_ATP: float) -> None:
        super().__init__(x, y)

        # Genome / Specie-dependent in the future
        self.MOVEMENT_SPEED: float = 10.0
        self.SIGHT_RANGE: float = 20.0
        self.MAX_HUNGER_NIBBLE = 0.3
        self.MAX_HUNGER_EAT = 0.7
        self.REPRODUCTION_ATP_TRESHOLD = 65
        self.MAX_ATP: float = MAX_ATP
        self.DIET: str = diet
        self.threat_factor: float = 1  # TODO make it dependent on its senses? + genome
        self.hormones: HormonalSystem = HormonalSystem()
        # Dependent on size, MAX_ATP, etc.
        self.caloric_value: float = 500

        # Dynamic attributes
        self.ATP: float = self.MAX_ATP * 0.9  # TODO Lower case!
        self.reproduction_timer: int = 100

        # Data attributes
        self.diet_in_sight: list
        self.memory: list = []  # TODO implement memory for plant locations

        # State-defining attributes
        self.is_alive: bool = True

    def _calculate_sight(self, population: Population) -> Population:
        creatures = [
            obj
            for obj in population.creatures
            if np.hypot(obj.x - self.x, obj.y - self.y) <= self.SIGHT_RANGE
        ]
        plants = [
            obj
            for obj in population.plants
            if np.hypot(obj.x - self.x, obj.y - self.y) <= self.SIGHT_RANGE
        ]
        consumables = [
            obj
            for obj in population.consumables
            if np.hypot(obj.x - self.x, obj.y - self.y) <= self.SIGHT_RANGE
        ]
        objs = creatures + plants + consumables
        objs = sorted(
            objs,
            key=self._distance,
        )  # By distance
        return Population(general=objs)

    def _update_diet(self) -> list[Creature,]:
        match self.DIET:
            case "carnivore":
                return self.sight_population.herbivores
            case "herbivore":
                return self.sight_population.consumables
            case _:
                return []

    def _calculate_path(self) -> tuple[float, float]:
        x_movement = 0
        y_movement = 0
        if self.goal.y > self.y:
            y_movement = 1
        elif self.goal.y < self.y:
            y_movement = -1
        if self.goal.x > self.x:
            x_movement = 1
        elif self.goal.x < self.x:
            x_movement = -1
        return (x_movement, y_movement)

    @staticmethod
    def _calculate_wander() -> tuple[float, float]:
        return (random.randint(-1, 1), random.randint(-1, 1))

    def _calculate_escape(self, obj: Object) -> tuple[float, float]:
        x_movement, y_movement = 0, 0
        if obj.x >= self.x:
            x_movement = -1
        elif obj.x < self.x:
            x_movement = 1
        if obj.y >= self.y:
            y_movement = -1
        elif obj.y < self.y:
            y_movement = 1
        return (x_movement, y_movement)

    def _can_reproduce(self) -> bool:
        if self.ATP < self.REPRODUCTION_ATP_TRESHOLD or self.reproduction_timer > 0:
            return False
        chance = 0.05 + 0.15 * (
            (self.ATP - self.REPRODUCTION_ATP_TRESHOLD) / 35
        )  # from 5% to 20%
        return random.random() < chance

    def _can_eat(self) -> bool:
        if not self.diet_in_sight:
            return False

        # self.hormones.gherlin *= 0.01
        return bool(
            random.random() < self.eating_urge
            and self.diet_in_sight[0].x - 2 < self.x < self.diet_in_sight[0].x + 2
            and self.diet_in_sight[0].y - 2 < self.y < self.diet_in_sight[0].y + 2,
        )  # probability rising with eating_urge

    def _can_goto(self) -> bool:
        if not self.diet_in_sight:
            return False
        return bool(
            self.diet_in_sight[0].x != self.x and self.diet_in_sight[0].y != self.y,
        )

    def _distance(self, obj: Object) -> float:
        return np.hypot(
            obj.x - self.x,
            obj.y - self.y,
        )  # Hypot - square root of substraction of squares

    def _should_escape(self, carnivores: list[Creature,]) -> bool:
        if not carnivores or self.DIET == "carnivore":
            return False
        closest_carnivore = carnivores[0]
        distance = max(0.1, self._distance(closest_carnivore))
        distance_normalized = distance / self.SIGHT_RANGE
        threat = min(1 / (1 + 10 * (distance_normalized) ** 3), 0.99)  # Rapid increase
        return random.random() < threat

    def _calculate_goal(self) -> Creature | Consumable:
        return self.diet_in_sight[0]  # Pick nearest

    def _action(self) -> Action:
        if self.ATP <= 0:
            return Action(type="die")
        if self._should_escape(
            self.sight_population.carnivores,
        ):  # TODO !!!: implement self._should_hunt() for predators(depending on hunger, factor)
            return Action(
                movement=self._calculate_escape(self.sight_population.carnivores[0]),
                type="escape",
            )
        if self._can_reproduce():
            return Action(type="reproduce", payload=self.reproduce())
        if self._can_eat():
            return Action(type="eat", payload=self.diet_in_sight[0])
        if self._can_goto():
            self.goal = self._calculate_goal()
            return Action(movement=self._calculate_path(), type="goto")
        return Action(movement=self._calculate_wander(), type="wander")

    def consume(self, obj: Creature | Consumable) -> float:
        hunger_strength: float = self.hormones.gherlin - self.hormones.leptin

        if hunger_strength < self.MAX_HUNGER_NIBBLE:
            # Nibble
            calories_eaten = min((self.MAX_ATP - self.ATP) * 0.4, obj.caloric_value)
            self.ATP = min(self.MAX_ATP, calories_eaten + self.ATP)
        elif hunger_strength < self.MAX_HUNGER_EAT:
            # Eat normally
            calories_eaten = min((self.MAX_ATP - self.ATP) * 0.9, obj.caloric_value)
            self.ATP = min(self.MAX_ATP, calories_eaten + self.ATP)
        else:
            # Overeat
            calories_eaten = min((self.MAX_ATP - self.ATP) * 1.5, obj.caloric_value)
            self.ATP = min(self.MAX_ATP, calories_eaten + self.ATP)
        # print(f"consumed: {calories_eaten}, ATP: {self.ATP}") TODO LOGGING!
        return calories_eaten

    def consumed(self, calories_consumed: float) -> bool:
        self.is_alive = False
        self.caloric_value -= calories_consumed
        return self.caloric_value <= 0

    def reproduce(self) -> Creature:
        self.ATP -= 35  # REPR_COST
        self.reproduction_timer = 60 * 10  # REPR_COOLDOWN
        spawn_offset = [-2, -1, 1, 2]
        return Creature(
            self.x + random.choice(spawn_offset),
            self.y + random.choice(spawn_offset),
            diet=self.DIET,
            MAX_ATP=self.MAX_ATP,
        )  # Spawn child with an offset

    def update(self, population: Population) -> Action:
        if not self.is_alive:
            return Action(type="dead")
        self.sight_population = self._calculate_sight(population=population)
        self.diet_in_sight = self._update_diet()
        self.eating_urge = self.hormones.update(current_atp=self.ATP, max_atp=100)
        action = self._action()
        self.ATP -= self.hormones.METABOLISM
        if self.reproduction_timer > 0:
            self.reproduction_timer -= 1
        return action


# Passionate Python
