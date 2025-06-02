from tkinter import Tk, ttk

import matplotlib.pyplot as plt
import pygame
import pygame_gui

WIDTH, HEIGHT = 100, 100
SCALE = 10
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
VIOLET = (127, 0, 255)
DARK_GRAY = (63, 63, 63)
BLUE = (0, 0, 255)
FPS = 30


class Statistics:
    def __init__(self) -> None:
        self.creatures_ot: list = []
        # self.creat

    def update(self, population) -> None:
        self.creatures_ot.append(len(population.creatures))


class Visualizer:
    def __init__(self) -> None:
        self.statistics = Statistics()
        self.figure, self.axis = self.__init_matplot()
        self.pg_screen, self.clock, self.ui_manager = self.__init_pygame()

    def __init_matplot(self):  # TODO: Type Annotations
        plt.ion()
        return plt.subplots(facecolor="#3f3f3f")

    def __init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
        clock = pygame.time.Clock()
        ui_manager = pygame_gui.UIManager((WIDTH * SCALE, HEIGHT * SCALE + 100))
        return screen, clock, ui_manager

    def __init_tk(self):
        tk_root = Tk(screenName="Ecosystem Simulation")
        tk_frm = ttk.Frame(
            tk_root,
            padding=10,
            width=WIDTH * SCALE + 100,
            height=HEIGHT * SCALE + 100,
        )
        tk_frm.grid()

    def _update_matplot(self, frame) -> None:
        if frame % FPS == 0:  # Matplotlib plot update every 1s
            self.axis.cla()
            self.axis.set_title("Creatures over time")
            self.axis.set_facecolor("#3f3f3f")
            self.axis.plot(self.statistics.creatures_ot)
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

    def _update_pygame(self, frame, population, time_delta) -> None:
        hello_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((350, 275), (100, 50)),
            text="Say Hello",
            manager=self.ui_manager,
        )
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                pygame.quit()
                raise RuntimeError
            self.ui_manager.process_events(event=event)
        self.ui_manager.update(time_delta=time_delta)
        self.pg_screen.fill(WHITE)
        self.ui_manager.draw_ui(self.pg_screen)

        for creature in population.herbivores:
            pygame.draw.circle(
                self.pg_screen,
                BLUE,
                (int(creature.x * SCALE), int(creature.y * SCALE)),
                SCALE,
            )  # creature.size
        for creature in population.carnivores:
            pygame.draw.circle(
                self.pg_screen,
                RED,
                (int(creature.x * SCALE), int(creature.y * SCALE)),
                SCALE,
            )  # creature.size
        for plant in population.plants:
            pygame.draw.circle(
                self.pg_screen,
                GREEN,
                (int(plant.x * SCALE), int(plant.y * SCALE)),
                SCALE,
            )  # creature.size
        for consumable in population.consumables:
            pygame.draw.circle(
                self.pg_screen,
                VIOLET,
                (int(consumable.x * SCALE), int(consumable.y * SCALE)),
                SCALE,
            )  # creature.size
        pygame.display.update()

    def update_loop(self, population, frame) -> None:
        time_delta = self.clock.tick(FPS)
        self.statistics.update(population)
        self._update_pygame(frame=frame, population=population, time_delta=time_delta)
        self._update_matplot(frame=frame)
