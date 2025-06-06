from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass

import numpy as np


@dataclass  # TODO Move Population to simulation.py?
class Population:  # TODO Inefficient property calling?
    general: list

    def __post_init__(self):
        self.categories: defaultdict = defaultdict(list)

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

    @property
    def corpses(self) -> list:
        return [obj for obj in self.general if isinstance(obj, Corpse)]

    def population_in_radius(
        self,
        center: Transform,
        radius: float,
    ) -> np.typing.NDArray:
        return np.array([
            obj
            for obj in self.general
            if np.hypot(obj.x - center.pos_x, obj.y - center.pos_y) <= radius
        ])  # Euclidean range


@dataclass
class Transform:
    pos_x: float = 0.0
    pos_y: float = 0.0

    rot_x: float = 0.0
    rot_y: float = 0.0

    scale_x: float = 0.0
    scale_y: float = 0.0


@dataclass
class Object:
    CATEGORY: str

    x: float
    y: float
    caloric_value: float


@dataclass(frozen=True)
class Action:
    movement: tuple[float, float] = (0.0, 0.0)
    type: str = ""
    payload: Creature | Plant | Consumable | None = None


@dataclass
class Corpse(Object):
    def update(self, population: Population) -> Action:
        return Action()


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
        super().__init__(CATEGORY="PLANT", x=x, y=y, caloric_value=1)
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
                CATEGORY="consumable",
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


class Creature(Object):  # TODO Decouple Sensory System
    def __init__(self, x: float, y: float, diet: str, MAX_ATP: float) -> None:
        super().__init__(CATEGORY="creature", x=x, y=y, caloric_value=500)

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
        self.atp: float = self.MAX_ATP * 0.9
        self.reproduction_timer: int = 100

        # Data attributes
        self.diet_in_sight: list
        self.memory: list = []  # TODO implement memory for plant locations

        # State-defining attributes
        self.is_alive: bool = True

    def _calculate_sight(self, population: Population) -> Population:
        objs = [
            obj
            for obj in population.general
            if np.hypot(obj.x - self.x, obj.y - self.y) <= self.SIGHT_RANGE
        ]
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

    def _calculate_movement(
        self,
        obj: Object,
        factor: int,
    ) -> np.typing.NDArray[np.float32]:
        direction = np.array(
            [obj.x - self.x, obj.y - self.y],
            dtype=np.float32,
        )  # TEMP [1, 2]
        norm: np.float32 = np.linalg.norm(
            direction,
        )  # Pythagoeran theorem # TEMP ar 1.6
        return (
            direction / norm * factor  # Direct movement
            if norm > 0  # If not, position is equal
            else np.array(
                self._calculate_wander(),
                dtype=np.float32,
            )  # TODO Convert arrays to np.array
        )

    @staticmethod
    def _calculate_wander() -> tuple[float, float]:
        return (random.randint(-1, 1), random.randint(-1, 1))

    def _can_reproduce(self) -> bool:
        if self.atp < self.REPRODUCTION_ATP_TRESHOLD or self.reproduction_timer > 0:
            return False
        chance = 0.05 + 0.15 * (
            (self.atp - self.REPRODUCTION_ATP_TRESHOLD) / 35
        )  # from 5% to 20%
        return random.random() < chance

    def _can_eat(self) -> bool:
        if not self.diet_in_sight:
            return False

        # self.hormones.gherlin *= 0.01
        return bool(
            random.random() < self.eating_urge
            and self._distance(obj=self.diet_in_sight[0])
            < 2,  # TODO Remove Magic Value!
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
        if self.atp <= 0:
            return Action(type="die")
        if self._should_escape(
            self.sight_population.carnivores,
        ):  # TODO: implement self._should_hunt() for predators(depending on hunger, factor)
            return Action(
                movement=self._calculate_movement(
                    obj=self.sight_population.carnivores[0],
                    factor=-1,
                ),
                type="escape",
            )
        if self._can_reproduce():
            return Action(type="reproduce", payload=self.reproduce())
        if self._can_eat():
            return Action(type="eat", payload=self.diet_in_sight[0])
        if self._can_goto():
            self.goal = self._calculate_goal()  # TODO cached or live goal?
            return Action(
                movement=self._calculate_movement(obj=self.goal, factor=1),
                type="goto",
            )
        return Action(movement=self._calculate_wander(), type="wander")

    def consume(self, obj: Creature | Consumable) -> float:
        hunger_strength: float = self.hormones.gherlin - self.hormones.leptin

        if hunger_strength < self.MAX_HUNGER_NIBBLE:
            # Nibble
            calories_eaten = min((self.MAX_ATP - self.atp) * 0.4, obj.caloric_value)
            self.atp = min(self.MAX_ATP, calories_eaten + self.atp)
        elif hunger_strength < self.MAX_HUNGER_EAT:
            # Eat normally
            calories_eaten = min((self.MAX_ATP - self.atp) * 0.9, obj.caloric_value)
            self.atp = min(self.MAX_ATP, calories_eaten + self.atp)
        else:
            # Overeat
            calories_eaten = min((self.MAX_ATP - self.atp) * 1.5, obj.caloric_value)
            self.atp = min(self.MAX_ATP, calories_eaten + self.atp)
        # print(f"consumed: {calories_eaten}, ATP: {self.atp}") TODO LOGGING!
        return calories_eaten

    def consumed(self, calories_consumed: float) -> bool:
        self.is_alive = False
        self.caloric_value -= calories_consumed
        return self.caloric_value <= 0

    def reproduce(self) -> Creature:
        self.atp -= 35  # REPR_COST
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
        self.eating_urge = self.hormones.update(current_atp=self.atp, max_atp=100)
        action = self._action()
        self.atp -= self.hormones.METABOLISM
        if self.reproduction_timer > 0:
            self.reproduction_timer -= 1
        return action
