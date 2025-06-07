from render import Render
from simulation import Simulation


class EcSim:
    def __init__(self) -> None:
        self.render = Render()
        self.simulation = Simulation()

    def main(self) -> None:
        frame = 0
        while True:
            self.simulation.update_environment()
            self.render.update(
                population=self.simulation.environment.population,
                frame=frame,
            )
            frame += 1


if __name__ == "__main__":
    ecsim = EcSim()
    ecsim.main()
