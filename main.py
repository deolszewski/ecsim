from simulation import Simulation
from visualization import Visualizer


class EcSim:
    def __init__(self) -> None:
        self.visualizer = Visualizer()
        self.simulation = Simulation()

    def main(self) -> None:
        frame = 0
        while True:
            self.simulation.update_environment()
            self.visualizer.update(
                population=self.simulation.environment.population,
                frame=frame,
            )
            frame += 1


if __name__ == "__main__":
    ecsim = EcSim()
    ecsim.main()
