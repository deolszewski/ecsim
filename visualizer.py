import os
import platform
import tkinter as tk
from tkinter import Tk, ttk

import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pygame.locals import RESIZABLE

from objects import Population

WIDTH, HEIGHT = 100, 100
SCALE = 10
WHITE = (255, 255, 255)  # TODO Convert all to HEX, and remove color constants
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

    def update(self, population: Population, frame: int) -> None:
        self.population = population
        self.frame = frame
        self.carnivores_ot.append(len(population.carnivores))
        self.herbivores_ot.append(len(population.herbivores))
        self.creatures_ot.append(len(population.creatures))
        self.eating_urge_ot.append(population.herbivores[0].eating_urge)
        self.gherlin_ot.append(population.herbivores[0].hormones.gherlin)
        self.leptin_ot.append(population.herbivores[0].hormones.leptin)
        self.atp_ot.append(population.herbivores[0].ATP)


class Visualizer:
    def __init__(self) -> None:
        self.FPS: float = 30.0

        self.root = Tk()
        self.root.title("Predator-Prey Simulation")

        self.statistics = Statistics()
        self.figure, self.axs = self.__init_matplot()

        self.__setup_tk_layout()
        self.__init_matplot_tk()

        self.pg_screen, self.clock = self.__init_pygame()

    @staticmethod
    def __init_matplot() -> tuple[Figure, list[Axes]]:
        plt.ioff()
        return plt.subplots(4)

    def __init_pygame(self) -> tuple[pygame.Surface, pygame.time.Clock]:
        # Env variables to make tk embedding work
        os.environ["SDL_WINDOWID"] = str(self.pygame_frame.winfo_id())
        if platform.system() == "Windows":
            os.environ["SDL_VIDEODRIVER"] = "windib"

        pygame.display.init()
        screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE), RESIZABLE)
        clock = pygame.time.Clock()
        return screen, clock

    def __setup_tk_layout(self) -> None:
        # Controls
        self.controls_frame = ttk.Frame(self.root, width=500)
        self.controls_frame.pack(padx=5, pady=5, fill=tk.BOTH, side=tk.LEFT)

        # FPS Slider
        self.fps_slider = tk.Scale(self.controls_frame, from_=1, to=200)
        self.fps_slider.pack(padx=5, pady=5, fill=tk.BOTH)
        self.fps_slider.set(30)

        # Pygame
        self.pygame_frame = ttk.Frame(
            self.root,
            height=HEIGHT * SCALE + 1,
            width=WIDTH * SCALE + 1,
        )
        self.pygame_frame.pack(padx=5, pady=5, fill=tk.BOTH, side=tk.LEFT)

        # Matplotlib plots
        self.matplot_frame = ttk.Frame(
            self.root,
            height=HEIGHT * SCALE,
            width=WIDTH * SCALE,
        )
        self.matplot_frame.pack(padx=5, pady=5, fill=tk.BOTH, side=tk.RIGHT)

    def __init_matplot_tk(self) -> None:
        canvas = FigureCanvasTkAgg(self.figure, master=self.matplot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
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
        if self.statistics.frame % self.FPS == 0:  # Matplotlib plot update every 1s
            for ax in self.axs:
                ax.cla()
            self._plot_axes()
            for ax in self.axs:
                ax.legend(loc=2)
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

    def _update_pygame(self) -> None:
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                pygame.quit()
                self.root.destroy()
                raise RuntimeError
        self.pg_screen.fill(WHITE)

        for creature in self.statistics.population.herbivores:
            pygame.draw.circle(
                self.pg_screen,
                BLUE,
                (int(creature.x * SCALE), int(creature.y * SCALE)),
                SCALE,
            )  # creature.size
        for creature in self.statistics.population.carnivores:
            pygame.draw.circle(
                self.pg_screen,
                RED,
                (int(creature.x * SCALE), int(creature.y * SCALE)),
                SCALE,
            )  # creature.size
        for plant in self.statistics.population.plants:
            pygame.draw.circle(
                self.pg_screen,
                GREEN,
                (int(plant.x * SCALE), int(plant.y * SCALE)),
                SCALE,
            )  # creature.size
        for consumable in self.statistics.population.consumables:
            pygame.draw.circle(
                self.pg_screen,
                VIOLET,
                (int(consumable.x * SCALE), int(consumable.y * SCALE)),
                SCALE,
            )  # creature.size
        pygame.display.flip()

    def _update_values(self) -> None:
        self.FPS = self.fps_slider.get()

    def update(self, population: Population, frame: int) -> None:
        self.statistics.update(population, frame)
        self._update_pygame()
        if frame % self.FPS == 0:
            self._update_matplot()
        self.root.update_idletasks()
        self.root.update()
        self._update_values()
        self.clock.tick(
            self.FPS,
        )  # TODO Wrong implementation, clock also viable for TK GUI which reduces its responsivity
