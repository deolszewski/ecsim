from simulation.objects import Population


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

    def update(self, selected_index, population: Population, frame: int) -> None:
        self.population = population
        self.frame = frame
        self.carnivores_ot.append(len(population.carnivores))
        self.herbivores_ot.append(len(population.herbivores))
        self.creatures_ot.append(len(population.creatures))
        self.eating_urge_ot.append(population.creatures[selected_index].eating_urge)
        self.gherlin_ot.append(population.creatures[selected_index].hormones.gherlin)
        self.leptin_ot.append(population.creatures[selected_index].hormones.leptin)
        self.atp_ot.append(population.creatures[selected_index].atp)

    def reset_selected(self) -> None:
        self.eating_urge_ot.clear()
        self.gherlin_ot.clear()
        self.leptin_ot.clear()
        self.atp_ot.clear()
