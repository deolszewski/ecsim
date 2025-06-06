import os
import platform
import tkinter as tk

import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from constants import Parameters
from objects import Population
from window import Window

WHITE = (255, 255, 255)  # TODO Convert all to HEX, remove color constants
RED = (255, 0, 0)
GREEN = (0, 128, 0)
VIOLET = (127, 0, 255)
DARK_GRAY = (63, 63, 63)
BLUE = (0, 0, 255)


class Statistics:
    def __init__(self) -> None:
        self.frame: int = 0
        self.population: Population = None

        self.creatures_ot: list = []
        self.herbivores_ot: list = []
        self.carnivores_ot: list = []
        self.eating_urge_ot: list = []
        self.gherlin_ot: list = []
        self.leptin_ot: list = []
        self.atp_ot: list = []

    def update(self, selected, population: Population, frame: int) -> None:
        self.population = population
        self.frame = frame
        self.carnivores_ot.append(len(population.carnivores))
        self.herbivores_ot.append(len(population.herbivores))
        self.creatures_ot.append(len(population.creatures))
        self.eating_urge_ot.append(population.general[0].eating_urge)
        self.gherlin_ot.append(population.general[0].hormones.gherlin)
        self.leptin_ot.append(population.general[0].hormones.leptin)
        self.atp_ot.append(population.general[0].atp)


class Visualizer:
    def __init__(self) -> None:
        self.FPS: float = 30.0

        self.root = Window()  # Tk window
        self.statistics = Statistics()
        self.figure, self.axs = self.__init_matplot()

        self.SCALE = self.root.HEIGHT / Parameters.ENV_HEIGHT  # for now x*x

        self.__init_matplot_tk()
        self.pg_screen, self.clock = self.__init_pygame()

    @staticmethod
    def __init_matplot() -> tuple[Figure, list[Axes]]:
        plt.ioff()
        plt.style.use("./resources/style/custom_dark.mplstyle")
        return plt.subplots(4)

    def __init_pygame(self) -> tuple[pygame.Surface, pygame.time.Clock]:
        # Env variables to make tk embedding work
        os.environ["SDL_WINDOWID"] = str(self.root.pygame_frame.winfo_id())
        if platform.system() == "Windows":
            os.environ["SDL_VIDEODRIVER"] = "windib"

        pygame.display.init()
        screen = pygame.display.set_mode()
        clock = pygame.time.Clock()
        return screen, clock

    def __init_matplot_tk(self) -> None:
        canvas = FigureCanvasTkAgg(self.figure, master=self.root.matplot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        for ax in self.axs:
            ax.legend()

    def _plot_axes(self) -> None:
        ticks = np.arange(self.statistics.frame + 1)

        self.axs[0].stackplot(
            ticks,
            np.vstack([self.statistics.herbivores_ot, self.statistics.carnivores_ot]),
            labels=["herbivore", "carnivore"],
        )
        self.axs[0].set_title("Environment Population")

        self.axs[1].plot(self.statistics.atp_ot, color="g", label="ATP")

        self.axs[3].stairs(
            self.statistics.gherlin_ot,
            color="#ffa500",
            label="gherlin",
        )
        self.axs[3].stairs(
            self.statistics.leptin_ot,
            color="#ffff00",
            label="leptin",
        )

        self.axs[2].plot(
            self.statistics.eating_urge_ot,
            color="r",
            label="eating urge",
        )

    def _update_matplot(self) -> None:
        if self.statistics.frame % self.FPS == 0:
            for ax in self.axs:
                ax.cla()
            self._plot_axes()
            for ax in self.axs:
                ax.legend(loc=4)
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

    def _update_pygame(self) -> None:
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                pygame.quit()
                self.root.destroy()
                raise RuntimeError
        self.pg_screen.fill("#1c1c1c")  # Gray-ish

        for creature in self.statistics.population.herbivores:
            pygame.draw.circle(
                self.pg_screen,
                BLUE,
                (int(creature.x * self.SCALE), int(creature.y * self.SCALE)),
                self.SCALE,
            )  # TODO creature.size
        for creature in self.statistics.population.carnivores:
            pygame.draw.circle(
                self.pg_screen,
                RED,
                (int(creature.x * self.SCALE), int(creature.y * self.SCALE)),
                self.SCALE,
            )
        for plant in self.statistics.population.plants:
            pygame.draw.circle(
                self.pg_screen,
                "#27d656",
                (int(plant.x * self.SCALE), int(plant.y * self.SCALE)),
                self.SCALE,
            )
        for consumable in self.statistics.population.consumables:
            pygame.draw.circle(
                self.pg_screen,
                VIOLET,
                (int(consumable.x * self.SCALE), int(consumable.y * self.SCALE)),
                self.SCALE,
            )
        pygame.display.flip()

    def _update_values(self) -> None:
        self.FPS = self.root.fps_slider.get()

    def update(self, population: Population, frame: int) -> None:
        self.statistics.update(selected="", population=population, frame=frame)
        self._update_pygame()
        if frame % self.FPS == 0:  # Plot refresh per 1s
            self._update_matplot()
        self.root.update_idletasks()
        self.root.update()
        self._update_values()
        self.clock.tick(
            self.FPS,
        )  # TODO Wrong implementation, clock also viable for TK GUI which reduces its responsivity
