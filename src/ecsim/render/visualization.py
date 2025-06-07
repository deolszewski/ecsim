import os
import platform
import tkinter as tk

import matplotlib.pyplot as plt
import numpy as np
import pygame
from config import Parameters
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from simulation.objects import Population

from .statistics import Statistics
from .window import Window


class Render:
    def __init__(self) -> None:
        self.FPS: float = 30.0
        self.selected_obj_index = 0

        self.root = Window(event_callback=self._handle_event)  # Tk window
        self.statistics = Statistics()
        self.figure, self.axs = self.__init_matplot()

        self.SCALE = self.root.HEIGHT / Parameters.ENV_HEIGHT - 1  # for now x*x

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
                "#4287f5",
                (int(creature.x * self.SCALE), int(creature.y * self.SCALE)),
                self.SCALE,
            )  # TODO creature.size
        for creature in self.statistics.population.carnivores:
            pygame.draw.circle(
                self.pg_screen,
                "#f54242",
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
                "#952aad",
                (int(consumable.x * self.SCALE), int(consumable.y * self.SCALE)),
                self.SCALE,
            )

        for corpse in self.statistics.population.corpses:
            pygame.draw.circle(
                self.pg_screen,
                "#9c9c9c",
                (int(corpse.x * self.SCALE), int(corpse.y * self.SCALE)),
                self.SCALE,
            )
        # Selected object
        pygame.draw.circle(
            self.pg_screen,
            "#ff9838",
            (
                int(
                    self.statistics.population.creatures[self.selected_obj_index].x
                    * self.SCALE,
                ),
                int(
                    self.statistics.population.creatures[self.selected_obj_index].y
                    * self.SCALE,
                ),
            ),
            self.SCALE,
        )
        pygame.display.flip()

    def _update_values(self) -> None:
        self.FPS = self.root.fps_slider.get()

    def _handle_event(self, event_type, *args) -> None:
        match event_type:
            case "next_object":
                self.statistics.reset_selected()
                if (
                    len(self.statistics.population.creatures) - 1
                    >= self.selected_obj_index + 1
                ):
                    self.selected_obj_index += 1
                else:
                    self.selected_obj_index = 0

    def update(self, population: Population, frame: int) -> None:
        self.statistics.update(
            selected_index=self.selected_obj_index,
            population=population,
            frame=frame,
        )
        self._update_pygame()
        if frame % self.FPS == 0:  # Plot refresh per 1s
            self._update_matplot()
        self.root.update_idletasks()
        self.root.update()
        self._update_values()
        self.clock.tick(
            self.FPS,
        )  # TODO Wrong implementation, clock also viable for TK GUI which reduces its responsivity
