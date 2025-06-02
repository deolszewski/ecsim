import random
from dataclasses import dataclass

import numpy as np


@dataclass
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

    def _poseq(self, other) -> bool:
        return other.x == self.x and other.y == self.y


class Plant(Object):
    def __init__(self, x, y) -> None:
        super().__init__(x, y)
        self.MAX_YIELD: int = random.randint(3, 15)
        self.current_yield: int = 0
        self.density: int = 10
        self.parent: list = []

    def update(self):
        return self.replicate()

    def yield_crops(self):
        if random.randint(1, 1000) == 1 and self.current_yield < self.MAX_YIELD:
            self.current_yield += 1
            return Consumable(
                x=random.randint(-1, 1) + self.x,
                y=random.randint(-1, 1) + self.y,
                parent=self,
            )
        return None

    def consumed(self) -> bool:
        self.density -= 1
        return not bool(self.density)  # Returns false if has some density left


@dataclass
class Consumable(Object):
    parent: Plant
    ATP: int = 40
    AMOUNT: int = random.randint(2, 7)

    def consumed(self) -> bool:
        self.AMOUNT -= 1
        if self.AMOUNT > 0:
            return False
        self.parent.current_yield -= 1
        return True


@dataclass
class Action:
    movement: tuple[int, int] = (0, 0)
    type: str = ""
    payload: Object = None


@dataclass
class HormonalSystem:
    LEPTIN_SENSITIVITY: float = 0.1
    GHERLIN_BASE: float = 0.3
    METABOLISM: float = 0.15

    leptin: float = 1  # Satiation hormone
    gherlin: float = 0  # Hunger hormone

    def update(self, current_atp, max_atp):
        self.leptin = self.LEPTIN_SENSITIVITY * current_atp
        self.gherlin = self.GHERLIN_BASE + (1 - current_atp / max_atp)

        # TODO: Sigmoid??
        eating_urge = 1 / (1 + np.exp(-10 * (self.gherlin - self.leptin)))
        return min(max(eating_urge, 0), 1)  # 0-1


class Creature(Object):
    def __init__(self, x, y, diet) -> None:
        super().__init__(x, y)
        self.MOVEMENT_SPEED = 10
        self.SIGHT_RANGE = 20

        self.hormones = HormonalSystem()
        self.MAX_ATP = 100
        self.ATP = 50

        self.DIET: str = diet
        self.diet_in_sight: list

        self.penalty = 0

        self.memory: list = []

        self.reproduction_timer = 100

    def _calculate_sight(self, population: Population) -> Population:
        creatures = [
            object
            for object in population.creatures
            if np.hypot(object.x - self.x, object.y - self.y) <= self.SIGHT_RANGE
        ]
        plants = [
            object
            for object in population.plants
            if np.hypot(object.x - self.x, object.y - self.y) <= self.SIGHT_RANGE
        ]
        consumables = [
            object
            for object in population.consumables
            if np.hypot(object.x - self.x, object.y - self.y) <= self.SIGHT_RANGE
        ]
        objs = creatures + plants + consumables
        objs = sorted(objs, key=lambda obj: np.hypot(obj.x - self.x, obj.y - self.y))
        return Population(general=objs)

    def _calculate_path(self):
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
        # if goal.y == self.x and goal.y == self.y:
        return (x_movement, y_movement)

    def _calculate_wander(self):
        return (random.randint(-1, 1), random.randint(-1, 1))

    def _update_diet(self, in_sight: Population):
        match self.DIET:
            case "carnivore":
                self.diet_in_sight = in_sight.herbivores
            case "herbivore":
                self.diet_in_sight = in_sight.consumables

    def _can_reproduce(self):
        if self.ATP < 65 or self.reproduction_timer > 0:
            return False
        chance = 0.05 + 0.15 * ((self.ATP - 65) / 35)  # from 5% to 20%
        return random.random() < chance

    def _can_eat(self):
        if random.random() < self.eating_urge:  # probability rising with eating_urge
            self.hormones.gherlin *= 0.01
            return True
        return False

    # TODO - remove that

    def consumed(self) -> bool:
        return True

    def reproduce(self):
        self.ATP -= 35  # REPR_COST
        self.reproduction_timer = 60 * 10  # REPR_COOLDOWN
        spawn_offset = [-2, -1, 1, 2]
        return Creature(
            self.x + random.choice(spawn_offset),
            self.y + random.choice(spawn_offset),
            diet=self.DIET,
        )  # Spawn child with an offset

    def _calc_goal(self):
        return self.diet_in_sight[0]  # Pick nearest

    def _action(self, in_sight) -> Action:
        if self.ATP <= 0:
            return Action(type="die")
        if self._can_reproduce():
            return Action(type="reproduce", payload=self.reproduce())
        if self._can_eat() and self.diet_in_sight:
            return Action(type="eat", payload=self.diet_in_sight[0])
        if not self.diet_in_sight:
            return Action(movement=self._calculate_wander(), type="wander")
        self.goal = self._calc_goal()
        return Action(movement=self._calculate_path(), type="goto")

    def update(self, population: Population) -> Action:
        sight_population = self._calculate_sight(population=population)
        self._update_diet(sight_population)
        self.eating_urge = self.hormones.update(current_atp=self.ATP, max_atp=100)
        action = self._action(in_sight=sight_population)
        self.ATP -= self.hormones.METABOLISM
        if self.reproduction_timer > 0:
            self.reproduction_timer -= 1
        return action


# Passionate Python
